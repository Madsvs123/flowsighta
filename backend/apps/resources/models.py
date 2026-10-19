from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Resource(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        PERSON = "person", "Person"
        EQUIPMENT = "equipment", "Equipment"
        FACILITY = "facility", "Facility"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        ALLOCATED = "allocated", "Allocated"
        UNAVAILABLE = "unavailable", "Unavailable"

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.PERSON)
    cost_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "type")
        indexes = [models.Index(fields=["organization", "type", "status"])]

    def __str__(self):
        return self.name


class ResourceSkill(TenantModel):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        EXPERT = "expert", "Expert"

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="skills")
    skill = models.CharField(max_length=120)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.INTERMEDIATE)

    class Meta:
        ordering = ["skill"]
        unique_together = ("organization", "resource", "skill")

    def __str__(self):
        return f"{self.resource.name} / {self.skill}"


class ResourceAllocation(TenantModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        CONFIRMED = "confirmed", "Confirmed"
        DONE = "done", "Done"

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="allocations")
    project_ref = models.CharField(max_length=64)
    start_date = models.DateField()
    end_date = models.DateField()
    hours_per_week = models.DecimalField(max_digits=6, decimal_places=2, default=40)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)

    class Meta:
        ordering = ["start_date"]
        indexes = [models.Index(fields=["organization", "resource", "status"])]

    def __str__(self):
        return f"{self.resource.name} / {self.project_ref}"


class ResourceCalendar(TenantModel):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="calendar")
    date = models.DateField()
    available_hours = models.DecimalField(max_digits=6, decimal_places=2, default=8)

    class Meta:
        ordering = ["date"]
        unique_together = ("organization", "resource", "date")

    def __str__(self):
        return f"{self.resource.name} / {self.date}"
