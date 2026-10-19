from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class AuditProgram(TenantModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    name = models.CharField(max_length=200)
    period = models.CharField(max_length=80, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNED, db_index=True
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "name")
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.name


class AuditEngagement(TenantModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    program = models.ForeignKey(
        AuditProgram, on_delete=models.CASCADE, related_name="engagements"
    )
    scope = models.CharField(max_length=255, blank=True)
    auditor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="audit_engagements",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNED, db_index=True
    )

    class Meta:
        ordering = ["-start_date"]
        indexes = [models.Index(fields=["organization", "program", "status"])]

    def __str__(self):
        return f"{self.scope or self.program.name} ({self.get_status_display()})"


class AuditFinding(TenantModel):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        REMEDIATED = "remediated", "Remediated"
        CLOSED = "closed", "Closed"

    engagement = models.ForeignKey(
        AuditEngagement, on_delete=models.CASCADE, related_name="findings"
    )
    severity = models.CharField(
        max_length=20, choices=Severity.choices, default=Severity.MEDIUM, db_index=True
    )
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True
    )

    class Meta:
        ordering = ["-severity", "status"]
        indexes = [models.Index(fields=["organization", "engagement", "status"])]

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.description[:60]}"


class AuditAction(TenantModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    finding = models.ForeignKey(AuditFinding, on_delete=models.CASCADE, related_name="actions")
    action = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_actions",
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True
    )

    class Meta:
        ordering = ["due_date", "action"]
        indexes = [models.Index(fields=["organization", "finding", "status"])]

    def __str__(self):
        return self.action
