from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class Incident(TenantModel):
    class Type(models.TextChoices):
        INJURY = "injury", "Injury"
        NEAR_MISS = "near_miss", "Near Miss"
        PROPERTY = "property", "Property Damage"
        ENVIRONMENTAL = "environmental", "Environmental"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        REPORTED = "reported", "Reported"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    number = models.CharField(max_length=40)
    date = models.DateField()
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.NEAR_MISS)
    severity = models.CharField(
        max_length=20, choices=Severity.choices, default=Severity.MEDIUM, db_index=True
    )
    location = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.REPORTED, db_index=True
    )

    class Meta:
        ordering = ["-date"]
        unique_together = ("organization", "number")
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "type", "severity"]),
        ]

    def __str__(self):
        return f"{self.number} ({self.get_type_display()})"


class IncidentInvestigation(TenantModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        COMPLETED = "completed", "Completed"

    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, related_name="investigations"
    )
    findings = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True
    )

    class Meta:
        ordering = ["-incident__date"]
        indexes = [models.Index(fields=["organization", "incident", "status"])]

    def __str__(self):
        return f"Investigation of {self.incident.number}"


class SafetyInspection(TenantModel):
    class Status(models.TextChoices):
        PASS = "pass", "Pass"
        FAIL = "fail", "Fail"
        CONDITIONAL = "conditional", "Conditional"

    location = models.CharField(max_length=160)
    date = models.DateField()
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="safety_inspections",
    )
    findings = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PASS, db_index=True
    )

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["organization", "location", "status"])]

    def __str__(self):
        return f"{self.location} — {self.get_status_display()} on {self.date}"


class SafetyTraining(TenantModel):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="safety_trainings",
    )
    topic = models.CharField(max_length=160)
    date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["organization", "employee", "expiry_date"])]

    def __str__(self):
        return f"{self.topic} — {self.employee}"
