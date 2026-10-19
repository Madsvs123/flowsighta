from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class CycleCount(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        FULL = "full", "Full"
        ABC = "abc", "ABC"
        RANDOM = "random", "Random"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        APPROVED = "approved", "Approved"

    number = models.CharField(max_length=60, blank=True)
    warehouse = models.ForeignKey(
        "organizations.Warehouse", on_delete=models.PROTECT, related_name="cycle_counts"
    )
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.ABC)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    scheduled_on = models.DateField(null=True, blank=True)
    counted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cycle_counts_counted",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "scheduled_on"])]

    def __str__(self):
        return self.number or str(self.id)


class CountLine(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        MATCHED = "matched", "Matched"
        VARIANCE = "variance", "Variance"
        RESOLVED = "resolved", "Resolved"

    count = models.ForeignKey(CycleCount, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="count_lines"
    )
    bin = models.CharField(max_length=60, blank=True)
    system_qty = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    counted_qty = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    variance = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["count__number", "id"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.count.number} · {self.product.sku}"
