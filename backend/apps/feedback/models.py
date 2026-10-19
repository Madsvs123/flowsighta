from django.db import models

from apps.core.models import AuditedModel, TenantModel


class FeedbackSurvey(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"

    title = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("organization", "status")

    def __str__(self):
        return self.title


class FeedbackResponse(TenantModel):
    survey = models.ForeignKey(
        FeedbackSurvey, on_delete=models.CASCADE, related_name="responses"
    )
    respondent_ref = models.CharField(max_length=120, blank=True)
    answers = models.JSONField(default=dict, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [models.Index(fields=["organization", "survey", "submitted_at"])]

    def __str__(self):
        return f"Response to {self.survey.title}"


class NpsScore(TenantModel):
    survey = models.ForeignKey(
        FeedbackSurvey, on_delete=models.CASCADE, related_name="nps_scores"
    )
    score = models.PositiveSmallIntegerField(default=0)
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [models.Index(fields=["organization", "survey", "score"])]

    def __str__(self):
        return f"NPS {self.score} on {self.survey.title}"


class Complaint(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    customer_ref = models.CharField(max_length=120, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    resolution = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.subject} ({self.customer_ref or '—'})"
