from django.db import models

from apps.core.models import AuditedModel, TenantModel


class CapacityProfile(TenantModel, AuditedModel):
    name = models.CharField(max_length=160)
    workcenter = models.CharField(max_length=120, blank=True)
    available_hours = models.DecimalField(max_digits=8, decimal_places=2, default=8)
    efficiency_pct = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "is_active"])]

    def __str__(self):
        return f"{self.name} ({self.workcenter})"


class CapacityLoad(TenantModel):
    profile = models.ForeignKey(CapacityProfile, on_delete=models.CASCADE, related_name="loads")
    date = models.DateField()
    load_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    available_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ["date"]
        unique_together = ("organization", "profile", "date")

    def __str__(self):
        return f"{self.profile.name} {self.date}: {self.load_hours}h"


class CapacityPlan(TenantModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    profile = models.ForeignKey(CapacityProfile, on_delete=models.CASCADE, related_name="plans")
    period_start = models.DateField()
    period_end = models.DateField()
    planned_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    utilization_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["period_start"]
        indexes = [models.Index(fields=["organization", "profile", "status"])]

    def __str__(self):
        return f"{self.profile.name} {self.period_start}..{self.period_end}"
