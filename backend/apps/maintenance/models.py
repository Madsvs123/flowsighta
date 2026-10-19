from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class Equipment(TenantModel):
    class Status(models.TextChoices):
        OPERATIONAL = "operational", "Operational"
        MAINTENANCE = "maintenance", "Maintenance"
        OUT_OF_SERVICE = "out_of_service", "Out of Service"

    code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=160, blank=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.OPERATIONAL
    )
    install_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("organization", "code")
        ordering = ["code"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.code} {self.name}"


class MaintenancePlan(TenantModel):
    class Type(models.TextChoices):
        PREVENTIVE = "preventive", "Preventive"
        PREDICTIVE = "predictive", "Predictive"
        CONDITION = "condition", "Condition"

    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="maintenance_plans"
    )
    frequency_days = models.PositiveIntegerField(default=30)
    type = models.CharField(
        max_length=20, choices=Type.choices, default=Type.PREVENTIVE
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["equipment__code", "id"]

    def __str__(self):
        return f"{self.equipment.code} · {self.type} · {self.frequency_days}d"


class MaintenanceOrder(TenantModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        OVERDUE = "overdue", "Overdue"

    plan = models.ForeignKey(
        MaintenancePlan,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="maintenance_orders"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SCHEDULED
    )
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-scheduled_date"]
        indexes = [models.Index(fields=["organization", "equipment", "status"])]

    def __str__(self):
        return f"{self.equipment.code} · {self.status} · {self.scheduled_date}"


class MaintenanceLog(TenantModel):
    order = models.ForeignKey(
        MaintenanceOrder, on_delete=models.CASCADE, related_name="logs"
    )
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="maintenance_logs",
    )
    hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order} · {self.hours}h"
