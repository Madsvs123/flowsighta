from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class VendorInvoice(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        RECEIVED = "received", "Received"
        IN_REVIEW = "in_review", "In Review"
        APPROVED = "approved", "Approved"
        PAID = "paid", "Paid"
        VOID = "void", "Void"

    number = models.CharField(max_length=40)
    supplier = models.ForeignKey(
        "suppliers.Supplier", on_delete=models.PROTECT, related_name="vendor_invoices"
    )
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED, db_index=True)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "due_date"])]

    @property
    def outstanding(self):
        if self.status != self.Status.PAID:
            return 0
        return self.total or 0

    def __str__(self):
        return f"{self.number} - {self.supplier.name}"


class VendorInvoiceLine(TenantModel):
    invoice = models.ForeignKey(VendorInvoice, on_delete=models.CASCADE, related_name="lines")
    description = models.CharField(max_length=240)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    rate = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    line_total = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.invoice.number} - {self.description}"


class InvoiceMatch(TenantModel):
    class ReferenceType(models.TextChoices):
        PURCHASE_ORDER = "purchase_order", "Purchase Order"
        GOODS_RECEIPT = "goods_receipt", "Goods Receipt"
        CONTRACT = "contract", "Contract"

    invoice_line = models.ForeignKey(VendorInvoiceLine, on_delete=models.CASCADE, related_name="matches")
    reference_type = models.CharField(max_length=30, choices=ReferenceType.choices, default=ReferenceType.PURCHASE_ORDER)
    reference_id = models.CharField(max_length=64, blank=True)
    matched_qty = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    variance = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.invoice_line} -> {self.reference_type}"


class InvoiceApproval(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    invoice = models.ForeignKey(VendorInvoice, on_delete=models.CASCADE, related_name="approvals")
    approver = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.CASCADE, related_name="invoice_approvals"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    comment = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.invoice.number} - {self.status}"
