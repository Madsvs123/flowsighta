from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class Rfq(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        AWARDED = "awarded", "Awarded"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=40)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "due_date"])]

    def __str__(self):
        return f"{self.number} - {self.title}"


class RfqLine(TenantModel):
    rfq = models.ForeignKey(Rfq, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", null=True, blank=True, on_delete=models.SET_NULL, related_name="rfq_lines"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    target_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta:
        ordering = ["-created_at"]

    @property
    def line_total(self):
        return (self.quantity or 0) * (self.target_price or 0)

    def __str__(self):
        product = self.product.sku if self.product else "?"
        return f"{self.rfq.number} - {product}"


class RfqResponse(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        WITHDRAWN = "withdrawn", "Withdrawn"

    rfq = models.ForeignKey(Rfq, on_delete=models.CASCADE, related_name="responses")
    supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.PROTECT, related_name="rfq_responses")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("organization", "rfq", "status")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rfq.number} - {self.supplier.name}"


class RfqResponseLine(TenantModel):
    response = models.ForeignKey(RfqResponse, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", null=True, blank=True, on_delete=models.SET_NULL, related_name="rfq_response_lines"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    delivery_days = models.PositiveIntegerField(null=True, blank=True)
    incoterm = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def line_total(self):
        return (self.quantity or 0) * (self.unit_price or 0)

    def __str__(self):
        product = self.product.sku if self.product else "?"
        return f"{self.response_id} - {product}"
