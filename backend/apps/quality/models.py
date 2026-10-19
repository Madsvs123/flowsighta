from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class QualityPlan(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    product = models.ForeignKey(
        "inventory.Product", on_delete=models.PROTECT, related_name="quality_plans"
    )
    name = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "product", "status"])]

    def __str__(self):
        return f"{self.product.sku} · {self.name}"


class QualityInspection(TenantModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"

    plan = models.ForeignKey(
        QualityPlan, on_delete=models.CASCADE, related_name="inspections"
    )
    reference = models.CharField(max_length=60)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SCHEDULED
    )
    inspected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="quality_inspections",
    )
    inspected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} ({self.status})"


class InspectionResult(TenantModel):
    inspection = models.ForeignKey(
        QualityInspection, on_delete=models.CASCADE, related_name="results"
    )
    attribute = models.CharField(max_length=120)
    value = models.CharField(max_length=120, blank=True)
    limit_min = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    limit_max = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    passed = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.inspection.reference} · {self.attribute}"


class NonConformance(TenantModel):
    class Type(models.TextChoices):
        MATERIAL = "material", "Material"
        PROCESS = "process", "Process"
        PACKAGING = "packaging", "Packaging"
        DOCUMENTATION = "documentation", "Documentation"

    class Severity(models.TextChoices):
        MINOR = "minor", "Minor"
        MAJOR = "major", "Major"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        DISPOSITIONED = "dispositioned", "Dispositioned"
        CLOSED = "closed", "Closed"

    reference = models.CharField(max_length=40)
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="non_conformances"
    )
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.MATERIAL)
    severity = models.CharField(
        max_length=20, choices=Severity.choices, default=Severity.MINOR
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True
    )
    description = models.TextField(blank=True)
    disposition = models.CharField(max_length=120, blank=True)

    class Meta:
        unique_together = ("organization", "reference")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "severity"])]

    def __str__(self):
        return f"{self.reference} · {self.product.sku}"


class CorrectiveAction(TenantModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        VERIFIED = "verified", "Verified"

    nc = models.ForeignKey(
        NonConformance, on_delete=models.CASCADE, related_name="corrective_actions"
    )
    action = models.CharField(max_length=300)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="corrective_actions",
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nc.reference} · {self.action}"
