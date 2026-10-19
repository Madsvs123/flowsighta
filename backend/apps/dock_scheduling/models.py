from django.db import models

from apps.core.models import TenantModel


class Dock(TenantModel):
    class Type(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND = "outbound", "Outbound"
        BOTH = "both", "Both"

    warehouse = models.ForeignKey(
        "organizations.Warehouse",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="docks",
    )
    code = models.CharField(max_length=40)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.BOTH)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "warehouse", "code")
        ordering = ["code"]

    def __str__(self):
        return self.code


class DockAppointment(TenantModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        ARRIVED = "arrived", "Arrived"
        LOADING = "loading", "Loading"
        COMPLETED = "completed", "Completed"
        NO_SHOW = "no_show", "No Show"

    dock = models.ForeignKey(Dock, on_delete=models.CASCADE, related_name="appointments")
    carrier = models.CharField(max_length=120, blank=True)
    vehicle = models.CharField(max_length=80, blank=True)
    driver = models.CharField(max_length=120, blank=True)
    window_start = models.DateField()
    window_end = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED, db_index=True)
    reference = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["window_start"]
        indexes = [models.Index(fields=["organization", "dock", "window_start"])]

    def __str__(self):
        return f"{self.dock.code} · {self.reference or self.vehicle}"
