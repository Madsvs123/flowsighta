from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class RiskRegister(TenantModel):
    class Impact(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Likelihood(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        IDENTIFIED = "identified", "Identified"
        ASSESSED = "assessed", "Assessed"
        MITIGATED = "mitigated", "Mitigated"
        ACCEPTED = "accepted", "Accepted"

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_risks",
    )
    impact = models.CharField(max_length=20, choices=Impact.choices, default=Impact.MEDIUM)
    likelihood = models.CharField(
        max_length=20, choices=Likelihood.choices, default=Likelihood.MEDIUM
    )
    score = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.IDENTIFIED, db_index=True
    )

    class Meta:
        ordering = ["-score", "name"]
        unique_together = ("organization", "name")
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "impact", "likelihood"]),
        ]

    def __str__(self):
        return self.name


class RiskAssessment(TenantModel):
    risk = models.ForeignKey(RiskRegister, on_delete=models.CASCADE, related_name="assessments")
    date = models.DateField()
    assessor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="risk_assessments",
    )
    impact = models.CharField(
        max_length=20, choices=RiskRegister.Impact.choices, default=RiskRegister.Impact.MEDIUM
    )
    likelihood = models.CharField(
        max_length=20,
        choices=RiskRegister.Likelihood.choices,
        default=RiskRegister.Likelihood.MEDIUM,
    )
    score = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["organization", "risk", "date"])]

    def __str__(self):
        return f"{self.risk.name} — score {self.score} on {self.date}"


class RiskMitigation(TenantModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    risk = models.ForeignKey(RiskRegister, on_delete=models.CASCADE, related_name="mitigations")
    action = models.CharField(max_length=255
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="risk_mitigations",
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True
    )

    class Meta:
        ordering = ["-due_date", "action"]
        indexes = [models.Index(fields=["organization", "risk", "status"])]

    def __str__(self):
        return self.action


class RiskReview(TenantModel):
    risk = models.ForeignKey(RiskRegister, on_delete=models.CASCADE, related_name="reviews")
    date = models.DateField()
    notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="risk_reviews",
    )

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["organization", "risk", "date"])]

    def __str__(self):
        return f"{self.risk.name} reviewed on {self.date}"
