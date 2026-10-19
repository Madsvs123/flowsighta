from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class ServiceOrder(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        INSTALLATION = "installation", "Installation"
        REPAIR = "repair", "Repair"
        MAINTENANCE = "maintenance", "Maintenance"
        INSPECTION = "inspection", "Inspection"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        DISPATCHED = "dispatched", "Dispatched"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=16)
    customer_ref = models.CharField(max_length=120, blank=True)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.REPAIR)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SCHEDULED
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_orders",
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("organization", "number")
        indexes = [models.Index(fields=["organization", "status", "scheduled_at"])]

    def __str__(self):
        return f"{self.number} · {self.customer_ref or self.get_type_display()}"


class ServiceLine(TenantModel):
    order = models.ForeignKey(
        ServiceOrder, on_delete=models.CASCADE, related_name="lines"
    )
    description = models.CharField(max_length=255)
    parts = models.JSONField(default=list, blank=True)
    labor_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.description} on {self.order.number}"


class ServiceAppointment(TenantModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CONFIRMED = "confirmed", "Confirmed"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    order = models.ForeignKey(
        ServiceOrder, on_delete=models.CASCADE, related_name="appointments"
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SCHEDULED
    )

    class Meta:
        ordering = ["start_at"]
        indexes = [models.Index(fields=["organization", "start_at", "status"])]

    def __str__(self):
        return f"Appointment for {self.order.number} at {self.start_at:%Y-%m-%d %H:%M}"


class FieldReport(TenantModel):
    order = models.ForeignKey(
        ServiceOrder, on_delete=models.CASCADE, related_name="field_reports"
    )
    notes = models.TextField(blank=True)
    findings = models.JSONField(default=dict, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"Field report for {self.order.number}"
