from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class ComplianceRequirement(TenantModel):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=120, blank=True)
    applies_to = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "name")
        indexes = [models.Index(fields=["organization", "category"])]

    def __str__(self):
        return self.name


class ComplianceCertificate(TenantModel):
    class Status(models.TextChoices):
        VALID = "valid", "Valid"
        EXPIRING = "expiring", "Expiring"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        related_name="compliance_certificates",
    )
    requirement = models.ForeignKey(
        ComplianceRequirement,
        on_delete=models.CASCADE,
        related_name="certificates",
    )
    number = models.CharField(max_length=80)
    issued_date = models.DateField(null=True, blank=True)
    expires_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.VALID, db_index=True
    )

    class Meta:
        ordering = ["-expires_date"]
        unique_together = ("organization", "number")
        indexes = [
            models.Index(fields=["organization", "supplier", "status"]),
            models.Index(fields=["organization", "expires_date"]),
        ]

    def __str__(self):
        return f"{self.number} ({self.requirement.name})"


class ComplianceAssessment(TenantModel):
    class Result(models.TextChoices):
        PASS = "pass", "Pass"
        FAIL = "fail", "Fail"
        CONDITIONAL = "conditional", "Conditional"

    certificate = models.ForeignKey(
        ComplianceCertificate,
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    date = models.DateField()
    result = models.CharField(max_length=20, choices=Result.choices, default=Result.PASS)
    notes = models.TextField(blank=True)
    assessor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="compliance_assessments",
    )

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["organization", "certificate", "result"])]

    def __str__(self):
        return f"{self.certificate.number} — {self.get_result_display()} on {self.date}"


class RegulatoryUpdate(TenantModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        EFFECTIVE = "effective", "Effective"
        SUPERSEDED = "superseded", "Superseded"

    title = models.CharField(max_length=200)
    region = models.CharField(max_length=80, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    summary = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PUBLISHED, db_index=True
    )

    class Meta:
        ordering = ["-effective_date"]
        indexes = [models.Index(fields=["organization", "region", "status"])]

    def __str__(self):
        return self.title
