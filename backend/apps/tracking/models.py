from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.core.models import AuditedModel, TenantModel


class TrackingEvent(TenantModel, AuditedModel):
    shipment = models.ForeignKey(
        "logistics.Shipment", on_delete=models.CASCADE, related_name="tracking_events_v2"
    )
    status = models.CharField(max_length=40, db_index=True)
    location = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    occurred_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["organization", "shipment", "occurred_at"])]

    def __str__(self):
        return f"{self.shipment.number} · {self.status}"


class GeoFence(TenantModel, AuditedModel):
    name = models.CharField(max_length=120)
    coordinates = models.JSONField(default=dict, blank=True)
    radius_m = models.PositiveIntegerField(default=500)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class GeofenceEvent(TenantModel):
    class Direction(models.TextChoices):
        ENTER = "enter", "Enter"
        EXIT = "exit", "Exit"

    fence = models.ForeignKey(GeoFence, on_delete=models.CASCADE, related_name="events")
    shipment = models.ForeignKey(
        "logistics.Shipment", null=True, blank=True, on_delete=models.SET_NULL, related_name="geofence_events"
    )
    direction = models.CharField(max_length=8, choices=Direction.choices, default=Direction.ENTER)
    occurred_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.fence.name} {self.direction}"


class EtaPrediction(TenantModel):
    shipment = models.ForeignKey(
        "logistics.Shipment", on_delete=models.CASCADE, related_name="eta_predictions"
    )
    eta = models.DateTimeField()
    confidence = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.7"))
    predicted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-predicted_at"]
        indexes = [models.Index(fields=["organization", "shipment", "-predicted_at"])]

    def __str__(self):
        return f"{self.shipment.number} ETA {self.eta}"
