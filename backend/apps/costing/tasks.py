import logging
from decimal import Decimal

from celery import shared_task
from django.utils import timezone

from apps.costing.models import InventoryValuation
from apps.inventory.models import StockItem

logger = logging.getLogger(__name__)


@shared_task
def recalculate_inventory_valuation():
    """Recompute total inventory value per warehouse from on-hand stock × unit cost."""
    rows = {}
    for item in (
        StockItem.objects.select_related("product", "warehouse")
        .only("organization_id", "warehouse_id", "on_hand", "product__unit_cost")
        .iterator(chunk_size=500)
    ):
        key = (item.organization_id, item.warehouse_id)
        agg = rows.setdefault(key, {"value": Decimal("0"), "count": 0})
        agg["value"] += (item.on_hand or 0) + (item.product.unit_cost or 0)
        agg["count"] += 1
    today = timezone.localdate()
    total = Decimal("0")
    written = 0
    for (org_id, warehouse_id), agg in rows.items():
        total += agg["value"]
        _, created = InventoryValuation.objects.update_or_create(
            organization_id=org_id,
            warehouse_id=warehouse_id,
            date=today,
            defaults={"total_value": agg["value"], "item_count": agg["count"]},
        )
        written += 1 if created else 0
    logger.info(
        "Recomputed inventory valuation for %s warehouses (total %s)",
        len(rows),
        total,
    )
    return {"warehouses": len(rows), "created": written, "total_value": float(total)}
