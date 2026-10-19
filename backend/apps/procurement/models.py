from decimal import Decimal

from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class Requisition(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        IN_APPROVAL = "in_approval", "In Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CONVERTED = "converted", "Converted"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=40)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    requester = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, related_name="requisitions"
    )
    warehouse = models.ForeignKey(
        "organizations.Warehouse", on_delete=models.SET_NULL, null=True, blank=True, related_name="requisitions"
    )
    needed_by = models.DateField(null=True, blank=True)
    justification = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="USD")

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]


class RequisitionLine(TenantModel):
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE, related_name="lines")
    sku = models.CharField(max_length=64)
    description = models.CharField(max_length=240)
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    uom = models.CharField(max_length=20, default="EA")
    estimated_unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    suggested_supplier = models.ForeignKey(
        "suppliers.Supplier", null=True, blank=True, on_delete=models.SET_NULL, related_name="requisition_lines"
    )
    needed_by = models.DateField(null=True, blank=True)

    @property
    def line_total(self):
        return (self.quantity or 0) * (self.estimated_unit_price or 0)


class ApprovalStep(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SKIPPED = "skipped", "Skipped"

    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE, related_name="approvals")
    sequence = models.PositiveIntegerField(default=1)
    approver = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="approval_steps"
    )
    approver_role = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    decided_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)


class PurchaseOrder(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        PARTIAL = "partial", "Partially Fulfilled"
        RECEIVED = "received", "Received"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=40)
    requisition = models.ForeignKey(
        Requisition, null=True, blank=True, on_delete=models.SET_NULL, related_name="purchase_orders"
    )
    supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.PROTECT, related_name="purchase_orders")
    warehouse = models.ForeignKey(
        "organizations.Warehouse", on_delete=models.SET_NULL, null=True, related_name="purchase_orders"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    currency = models.CharField(max_length=8, default="USD")
    payment_terms = models.CharField(max_length=40, blank=True)
    incoterms = models.CharField(max_length=20, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    freight_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "expected_delivery_date"])]


class PurchaseOrderLine(TenantModel):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="lines")
    sku = models.CharField(max_length=64)
    description = models.CharField(max_length=240)
    quantity_ordered = models.DecimalField(max_digits=14, decimal_places=3)
    quantity_received = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    quantity_cancelled = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    quantity_backordered = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    uom = models.CharField(max_length=20, default="EA")
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    expected_delivery_date = models.DateField(null=True, blank=True)
    warehouse = models.ForeignKey(
        "organizations.Warehouse", null=True, blank=True, on_delete=models.SET_NULL, related_name="po_lines"
    )
    product = models.ForeignKey(
        "inventory.Product", null=True, blank=True, on_delete=models.SET_NULL, related_name="po_lines"
    )

    @property
    def quantity_open(self):
        return (
            (self.quantity_ordered or Decimal("0"))
            - (self.quantity_received or Decimal("0"))
            - (self.quantity_cancelled or Decimal("0"))
        )

    @property
    def line_total(self):
        return (self.quantity_ordered or 0) * (self.unit_price or 0)

    @property
    def fulfillment_status(self):
        if self.quantity_cancelled >= self.quantity_ordered:
            return "cancelled"
        if self.quantity_received < 0:
            return "open"
        if self.quantity_received < self.quantity_cancelled:
            return "partial"
        return "received"


class POStatusHistory(TenantModel):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    changed_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)


class GoodsReceipt(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        POSTED = "posted", "Posted"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=40)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="receipts")
    warehouse = models.ForeignKey("organizations.Warehouse", on_delete=models.PROTECT, related_name="receipts")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    received_at = models.DateTimeField(null=True, blank=True)
    packing_slip = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "number")


class GoodsReceiptLine(TenantModel):
    receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name="lines")
    po_line = models.ForeignKey(PurchaseOrderLine, on_delete=models.PROTECT, related_name="receipt_lines")
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    quantity_damaged = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    batch_number = models.CharField(max_length=60, blank=True)
    location = models.ForeignKey(
        "organizations.Location", null=True, blank=True, on_delete=models.SET_NULL, related_name="receipt_lines"
    )


class Backorder(TenantModel):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="backorders")
    po_line = models.ForeignKey(PurchaseOrderLine, on_delete=models.CASCADE, related_name="backorders")
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    promised_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default="open")
    notes = models.TextField(blank=True)
