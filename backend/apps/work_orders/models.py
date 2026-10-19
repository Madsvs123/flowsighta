from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class WorkOrder(TenantModel):
    class Type(models.TextChoices):
        MAINTENANCE = "maintenance", "Maintenance"
        REPAIR = "repair", "Repair"
        IMPROVEMENT = "improvement", "Improvement"
        INSPECTION = "inspection", "Inspection"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In Progress"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    number = models.CharField(max_length=40)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.MAINTENANCE)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="work_orders",
    )
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "priority"])]

    def __str__(self):
        return f"{self.number} ({self.type})"


class WorkOrderTask(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="tasks")
    description = models.CharField(max_length=300)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    duration_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.order.number} · {self.description}"


class WorkOrderLabor(TenantModel):
    order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="labor")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="work_order_labor",
    )
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.order.number} · {self.user} · {self.hours}h"
