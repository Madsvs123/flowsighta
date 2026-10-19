from django.db import models

from apps.core.models import TenantModel


class YardLocation(TenantModel):
    class Type(models.TextChoices):
        STAGING = "staging", "Staging"
        SPOT = "spot", "Spot"
        PARKING = "parking", "Parking"

    warehouse = models.ForeignKey(
        "organizations.Warehouse",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="yard_locations",
    )
    code = models.CharField(max_length=40)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.STAGING)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "warehouse", "code")
        ordering = ["code"]

    def __str__(self):
        return self.code


class YardMove(TenantModel):
    class Direction(models.TextChoices):
        IN = "in", "In"
        OUT = "out", "Out"

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        MOVING = "moving", "Moving"
        PARKED = "parked", "Parked"
        DEPARTED = "departed", "Departed"

    location = models.ForeignKey(YardLocation, on_delete=models.CASCADE, related_name="moves")
    vehicle = models.CharField(max_length=80, blank=True)
    trailer = models.CharField(max_length=80, blank=True)
    direction = models.CharField(max_length=10, choices=Direction.choices, default=Direction.IN)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED, db_index=True)
    moved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.vehicle or 'vehicle'} @ {self.location.code}"


class YardGateLog(TenantModel):
    class Direction(models.TextChoices):
        IN = "in", "In"
        OUT = "out", "Out"

    vehicle = models.CharField(max_length=80, blank=True)
    trailer = models.CharField(max_length=80, blank=True)
    direction = models.CharField(max_length=10, choices=Direction.choices, default=Direction.IN)
    driver = models.CharField(max_length=120, blank=True)
    occurred_at = models.DateTimeField()
    gate = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["organization", "occurred_at"])]

    def __str__(self):
        return f"{self.vehicle or 'vehicle'} {self.direction} @ {self.gate or 'gate'}"
