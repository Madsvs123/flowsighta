from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Vehicle(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        VAN = "van", "Van"
        TRUCK = "truck", "Truck"
        TRAILER = "trailer", "Trailer"
        FORKLIFT = "forklift", "Forklift"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        MAINTENANCE = "maintenance", "Maintenance"
        OUT_OF_SERVICE = "out_of_service", "Out of Service"
        RETIRED = "retired", "Retired"

    plate = models.CharField(max_length=24)
    type = models.CharField(max_length=16, choices=Type.choices, default=Type.TRUCK)
    capacity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    odometer = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["plates"]
        unique_together = ("organization", "plate")
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.plate} ({self.type})"


class Driver(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPENDED = "suspended", "Suspended"

    name = models.CharField(max_length=160)
    license_number = models.CharField(max_length=60, blank=True)
    license_class = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE, db_index=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.name


class VehicleMaintenance(TenantModel):
    class Type(models.TextChoices):
        PREVENTIVE = "preventive", "Preventive"
        REPAIR = "repair", "Repair"
        INSPECTION = "inspection", "Inspection"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="maintenance_records")
    type = models.CharField(max_length=16, choices=Type.choices, default=Type.PREVENTIVE)
    odometer = models.PositiveIntegerField(default=0)
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SCHEDULED, db_index=True)

    class Meta:
        ordering = ["-scheduled_date", "-created_at"]
        indexes = [models.Index(fields=["organization", "status", "scheduled_date"])]

    def __str__(self):
        return f"{self.vehicle.plate} {self.type}"


class FuelLog(TenantModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="fuel_logs")
    date = models.DateField(db_index=True)
    gallons = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    odometer = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [models.Index(fields=["organization", "vehicle", "date"])]

    def __str__(self):
        return f"{self.vehicle.plate} {self.date} {self.gallons}"
