from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class ProductionOrder(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        RELEASED = "released", "Released"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    number = models.CharField(max_length=40)
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="production_orders"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.number} {self.product.name}"


class ProductionStep(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    order = models.ForeignKey(
        ProductionOrder, on_delete=models.CASCADE, related_name="steps"
    )
    sequence = models.PositiveIntegerField(default=1)
    operation = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        ordering = ["-sequence"]

    def __str__(self):
        return f"{self.order.number} · {self.sequence} {self.operation}"


class ProductionOutput(TenantModel):
    order = models.ForeignKey(
        ProductionOrder, on_delete=models.CASCADE, related_name="outputs"
    )
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="production_outputs"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    batch_number = models.CharField(max_length=60, blank=True)
    produced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-produced_at"]

    def __str__(self):
        return f"{self.order.number} · {self.product.sku} × {self.quantity}"


class MaterialIssue(TenantModel):
    order = models.ForeignKey(
        ProductionOrder, on_delete=models.CASCADE, related_name="material_issues"
    )
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="material_issues"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    from_bin = models.CharField(max_length=60, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="material_issues",
    )

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return f"{self.order.number} · {self.product.sku} × {self.quantity}"
