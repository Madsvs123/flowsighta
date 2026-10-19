from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class PickWave(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        RELEASED = "released", "Released"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    number = models.CharField(max_length=60, blank=True)
    warehouse = models.ForeignKey(
        "organizations.Warehouse", on_delete=models.CASCADE, related_name="pick_waves"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "priority"])]

    def __str__(self):
        return self.number or str(self.id)


class PickLine(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PICKED = "picked", "Picked"
        SHORT = "short", "Short"
        SKIPPED = "skipped", "Skipped"

    wave = models.ForeignKey(PickWave, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="pick_lines"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    from_bin = models.CharField(max_length=60, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["wave__number", "id"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.wave.number} · {self.product.sku}"


class PickTask(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    wave = models.ForeignKey(PickWave, on_delete=models.CASCADE, related_name="tasks")
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="pick_tasks",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"Task {self.wave.number} · {self.status}"
