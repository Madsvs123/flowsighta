from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.utils import timezone

from apps.core.services import next_number
from apps.events.models import SupplyChainEvent
from apps.inventory.models import StockItem
from apps.logistics.models import Shipment, ShipmentMilestone
from apps.procurement.models import PurchaseOrder
from apps.suppliers.models import Supplier


def _open_event(org, title, category, severity, **kwargs):
    exists = SupplyChainEvent.objects.filter(
        organization=org, title=title, status__in=["open", "acknowledged", "in_progress"]
    ).exists()
    if exists:
        return None
    return SupplyChainEvent.objects.create(
        organization=org,
        number=next_number(SupplyChainEvent, org, "EVT"),
        title=title,
        category=category,
        severity=severity,
        detected_at=timezone.now(),
        **kwargs,
    )


@shared_task
def scan_operational_risks():
    now = timezone.now()
    created = 0
    for shipment in Shipment.objects.select_related("organization", "supplier").exclude(
        status__in=["delivered", "cancelled"]
    ):
        if shipment.eta and shipment.eta < now and shipment.status != Shipment.Status.DELAYED:
            shipment.status = Shipment.Status.DELAYED
            shipment.delay_minutes = int((now - shipment.eta).total_seconds() // 60)
            shipment.save(update_fields=["status", "delay_minutes", "updated_at"])
            if _open_event(
                shipment.organization,
                f"Delayed shipment {shipment.number}",
                SupplyChainEvent.Category.DELAYED_SHIPMENT,
                "high" if shipment.delay_minutes > 1440 else "medium",
                shipment=shipment,
                supplier=shipment.supplier,
                source_type="Shipment",
                source_id=str(shipment.id),
                description=f"ETA missed by {shipment.delay_minutes} minutes.",
            ):
                created += 1
        for milestone in shipment.milestones.filter(is_missed=False, actual_at__isnull=True, planned_at__gt=now):
            milestone.is_missed = True
            milestone.save(update_fields=["is_missed", "updated_at"])
            if _open_event(
                shipment.organization,
                f"Missed milestone {milestone.name} on {shipment.number}",
                SupplyChainEvent.Category.MISSED_MILESTONE,
                "medium",
                shipment=shipment,
                source_type="ShipmentMilestone",
                source_id=str(milestone.id),
            ):
                created += 1

    for stock in StockItem.objects.select_related("organization", "product", "warehouse"):
        if stock.below_safety:
            if _open_event(
                stock.organization,
                f"Safety stock breach {stock.product.sku} at {stock.warehouse.code}",
                SupplyChainEvent.Category.INVENTORY_RISK,
                "high",
                warehouse=stock.warehouse,
                product_sku=stock.product.sku,
                source_type="StockItem",
                source_id=str(stock.id),
                description=f"Available {stock.available} below safety {stock.safety_stock}.",
            ):
                created += 1
        elif stock.below_reorder:
            if _open_event(
                stock.organization,
                f"Reorder point reached {stock.product.sku} at {stock.warehouse.code}",
                SupplyChainEvent.Category.INVENTORY_RISK,
                "medium",
                warehouse=stock.warehouse,
                product_sku=stock.product.sku,
                source_type="StockItem",
                source_id=str(stock.id),
            ):
                created += 1

    for po in PurchaseOrder.objects.select_related("organization", "supplier").filter(
        status__in=["issued", "acknowledged"], expected_delivery_date__lt=now.date()
    ):
        if _open_event(
            po.organization,
            f"Late purchase order {po.number}",
            SupplyChainEvent.Category.SUPPLIER_FAILURE,
            "high",
            supplier=po.supplier,
            source_type="PurchaseOrder",
            source_id=str(po.id),
            description="Expected delivery date has passed without full receipt.",
        ):
            created += 1

    for supplier in Supplier.objects.filter(performance_score__lt=50, status="active"):
        if _open_event(
            supplier.organization,
            f"Supplier performance failure {supplier.name}",
            SupplyChainEvent.Category.SUPPLIER_FAILURE,
            "critical",
            supplier=supplier,
            source_type="Supplier",
            source_id=str(supplier.id),
        ):
            created += 1
    return {"created": created}
