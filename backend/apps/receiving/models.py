from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Receipt(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        EXPECTED = "expected", "Expected"
        IN_PROGRESS = "in_progress", "In Progress"
        RECEIVED = "received", "Received"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=20, blank=True)
    supplier = models.ForeignKey(
        "suppliers.Supplier", null=True, blank=True, on_delete=models.SET_NULL, related_name="receipts"
    )
    warehouse = models.ForeignKey(
        "organizations.Warehouse", on_delete=models.CASCADE, related_name="receipts"
    )
    reference = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EXPECTED)
    received_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.number or str(self.id)


class ReceiptLine(TenantModel):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="receipt_lines"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    received_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    batch_number = models.CharField(max_length=60, blank=True)
    expires_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["receipt__number", "id"]
        indexes = [models.Index(fields=["organization", "product"])]

    def __str__(self):
        return f"{self.receipt.number} · {self.product.sku}"


class PutawayTask(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    receipt_line = models.ForeignKey(
        ReceiptLine, on_delete=models.CASCADE, related_name="putaway_tasks"
    )
    bin = models.ForeignKey(
        "warehousing.Bin", null=True, blank=True, on_delete=models.SET_NULL, related_name="putaway_tasks"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_putaway_tasks",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"Putaway {self.receipt_line_id} · {self.status}"
