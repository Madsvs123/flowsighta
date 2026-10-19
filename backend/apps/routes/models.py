from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Route(TenantModel, AuditedModel):
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=160)
    origin = models.CharField(max_length=160, blank=True
    destination = models.CharField(max_length=160, blank=True)
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        unique_together = ("organization", "code")

    def __str__(self):
        return f"{self.code} {self.name}".strip()


class RouteStop(TenantModel):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="stops")
    sequence = models.PositiveIntegerField(default=1)
    location_name = models.CharField(max_length=160)
    eta_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["route", "sequence"]
        unique_together = ("route", "sequence")

    def __str__(self):
        return f"{self.route.code} #{self.sequence} {self.location_name}"


class DriverAssignment(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="assignments")
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="route_assignments"
    )
    vehicle = models.CharField(max_length=60, blank=True)
    scheduled_date = models.DateField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ASSIGNED, db_index=True)

    class Meta:
        ordering = ["scheduled_date", "-created_at"]
        indexes = [models.Index(fields=["organization", "status", "scheduled_date"])]

    def __str__(self):
        return f"{self.route.code} → {self.driver.full_name or self.driver.email}"


class DeliveryStop(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ARRIVED = "arrived", "Arrived"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="deliveries")
    address = models.CharField(max_length=240, blank=True)
    contact = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    pod_reference = models.CharField(max_length=80, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["route", "created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.route.code} {self.address or self.contact}"
