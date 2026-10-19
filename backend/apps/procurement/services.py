from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.core.realtime import publish_organization_event
from apps.core.services import log_activity, next_number
from apps.inventory.models import InventoryMovement, Product, StockItem
from apps.procurement.models import (
    ApprovalStep,
    Backorder,
    GoodsReceipt,
    POStatusHistory,
    PurchaseOrder,
    PurchaseOrderLine,
    Requisition,
)
from apps.suppliers.models import PurchaseHistory


def record_po_status(po, to_status, user, note=""):
    POStatusHistory.objects.create(
        organization=po.organization,
        purchase_order=po,
        from_status=po.status,
        to_status=to_status,
        note=note,
        changed_by=user,
    )
    po.status = to_status
    po.save(update_fields=["status", "updated_at"])
    publish_organization_event(
        po.organization_id, "purchase_order", {"id": str(po.id), "number": po.number, "status": to_status}
    )
    log_activity(po.organization, user, "status_change", "PurchaseOrder", po.id, f"{po.number} → {to_status}")


@transaction.atomic
def submit_requisition(requisition, user):
    requisition.status = Requisition.Status.IN_APPROVAL
    requisition.save(update_fields=["status", "updated_at"])
    if not requisition.approvals.exists():
        ApprovalStep.objects.create(
            organization=requisition.organization,
            requisition=requisition,
            sequence=1,
            approver=user,
            approver_role="Procurement Manager",
            status=ApprovalStep.Status.PENDING,
        )
    return requisition


@transaction.atomic
def decide_approval(step, user, approved, comment=""):
    step.status = ApprovalStep.Status.APPROVED if approved else ApprovalStep.Status.REJECTED
    step.approver = user
    step.decided_at = timezone.now()
    step.comment = comment
    step.save()
    req = step.requisition
    if not approved:
        req.status = Requisition.Status.REJECTED
        req.save(update_fields=["status", "updated_at"])
        return req
    pending = req.approvals.filter(status=ApprovalStep.Status.PENDING).exists()
    if not pending:
        req.status = Requisition.Status.APPROVED
        req.save(update_fields=["status", "updated_at"])
    return req


@transaction.atomic
def convert_requisition(requisition, supplier, user):
    po = PurchaseOrder.objects.create(
        organization=requisition.organization,
        number=next_number(PurchaseOrder, requisition.organization, "PO"),
        requisition=requisition,
        supplier=supplier,
        warehouse=requisition.warehouse,
        currency=requisition.currency,
        expected_delivery_date=requisition.needed_by,
        created_by=user,
        updated_by=user,
        notes=requisition.justification,
    )
    subtotal = Decimal("0")
    for line in requisition.lines.all():
        product = Product.objects.filter(organization=requisition.organization, sku=line.sku).first()
        pol = PurchaseOrderLine.objects.create(
            organization=requisition.organization,
            purchase_order=po,
            sku=line.sku,
            description=line.description,
            quantity_ordered=line.quantity,
            uom=line.uom,
            unit_price=line.estimated_unit_price,
            expected_delivery_date=line.needed_by or requisition.needed_by,
            warehouse=requisition.warehouse,
            product=product,
        )
        subtotal += Decimal(str(pol.line_total))
    po.subtotal = subtotal
    po.total_amount = subtotal
    po.save(update_fields=["subtotal", "total_amount"])
    requisition.status = Requisition.Status.CONVERTED
    requisition.save(update_fields=["status", "updated_at"])
    record_po_status(po, PurchaseOrder.Status.DRAFT, user, "Converted from requisition")
    return po


@transaction.atomic
def issue_purchase_order(po, user):
    po.issued_at = timezone.now()
    po.save(update_fields=["issued_at"])
    record_po_status(po, PurchaseOrder.Status.ISSUED, user, "Issued to supplier")
    for line in po.lines.all():
        if line.product_id and po.warehouse_id:
            stock, _ = StockItem.objects.get_or_create(
                organization=po.organization,
                product=line.product,
                warehouse=po.warehouse,
                location=None,
                defaults={},
            )
            stock.incoming += line.quantity_ordered
            stock.save(update_fields=["incoming"])
    return po


@transaction.atomic
def cancel_purchase_order(po, user, reason=""):
    po.cancelled_at = timezone.now()
    po.cancellation_reason = reason
    po.save(update_fields=["cancelled_at", "cancellation_reason"])
    for line in po.lines.all():
        remaining = line.quantity_open
        line.quantity_cancelled = (line.quantity_cancelled or 0) + remaining
        line.save(update_fields=["quantity_cancelled"])
        if line.product_id and po.warehouse_id and po.status in (PurchaseOrder.Status.ISSUED, PurchaseOrder.Status.ACKNOWLEDGED, PurchaseOrder.Status.PARTIAL):
            stock = StockItem.objects.filter(
                organization=po.organization, product=line.product, warehouse=po.warehouse, location__isnull=True
            ).first()
            if stock:
                stock.incoming = max(Decimal("0"), (stock.incoming or 0) - remaining)
                stock.save(update_fields=["incoming"])
    record_po_status(po, PurchaseOrder.Status.CANCELLED, user, reason)
    return po


@transaction.atomic
def post_goods_receipt(receipt, user):
    receipt.status = GoodsReceipt.Status.POSTED
    receipt.received_at = timezone.now()
    receipt.save(update_fields=["status", "received_at", "updated_at"])
    po = receipt.purchase_order
    for line in receipt.lines.select_related("po_line"):
        pol = line.po_line
        good_qty = (line.quantity or 0) - (line.quantity_damaged or 0)
        pol.quantity_received = (pol.quantity_received or 0) + (line.quantity or 0)
        if line.quantity_damaged:
            pol.quantity_backordered = (pol.quantity_backordered or 0) + line.quantity_damaged
            Backorder.objects.create(
                organization=po.organization,
                purchase_order=po,
                po_line=pol,
                quantity=line.quantity_damaged,
                status="open",
                notes="Damaged on receipt",
            )
        pol.save(update_fields=["quantity_received", "quantity_backordered"])
        product = pol.product or Product.objects.filter(organization=po.organization, sku=pol.sku).first()
        if product:
            stock, _ = StockItem.objects.get_or_create(
                organization=po.organization,
                product=product,
                warehouse=receipt.warehouse,
                location=line.location,
                defaults={},
            )
            stock.on_hand += line.quantity
            stock.incoming = max(Decimal("0"), (stock.incoming or 0) - (line.quantity or 0))
            stock.save(update_fields=["on_hand", "incoming"])
            InventoryMovement.objects.create(
                organization=po.organization,
                product=product,
                warehouse=receipt.warehouse,
                to_location=line.location,
                kind=InventoryMovement.Kind.RECEIPT,
                quantity=good_qty,
                reference_type="GoodsReceipt",
                reference_id=str(receipt.id),
                batch_number=line.batch_number,
                occurred_at=receipt.received_at,
                created_by=user,
            )
    all_received = all(l.quantity_received >= l.quantity_ordered for l in po.lines.all())
    any_received = any(l.quantity_received > 0 for l in po.lines.all())
    if all_received:
        record_po_status(po, PurchaseOrder.Status.RECEIVED, user, "Fully received")
        PurchaseHistory.objects.create(
            organization=po.organization,
            supplier=po.supplier,
            purchase_order_number=po.number,
            ordered_on=(po.issued_at or po.created_at).date(),
            received_on=timezone.now().date(),
            amount=po.total_amount,
            currency=po.currency,
            on_time=True if not po.expected_delivery_date else timezone.now().date() <= po.expected_delivery_date,
        )
    elif any_received:
        record_po_status(po, PurchaseOrder.Status.PARTIAL, user, "Partial receipt posted")
        for pol in po.lines.all():
            open_qty = pol.quantity_open
            if open_qty > 0 and not pol.backorders.filter(status="open").exists():
                pol.quantity_backordered = open_qty
                pol.save(update_fields=["quantity_backordered"])
                Backorder.objects.create(
                    organization=po.organization,
                    purchase_order=po,
                    po_line=pol,
                    quantity=open_qty,
                    promised_date=po.expected_delivery_date,
                    status="open",
                )
    return receipt
