from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class JobPosting(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        ON_HOLD = "on_hold", "On Hold"
        CLOSED = "closed", "Closed"

    title = models.CharField(max_length=200)
    department = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    openings = models.PositiveIntegerField(default=1)
    salary_range = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.title


class Candidate(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        SCREENED = "screened", "Screened"
        INTERVIEWED = "interviewed", "Interviewed"
        OFFERED = "offered", "Offered"
        HIRED = "hired", "Hired"
        REJECTED = "rejected", "Rejected"

    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    source = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.name


class Application(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        SCREENING = "screening", "Screening"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"
        HIRED = "hired", "Hired"
        REJECTED = "rejected", "Rejected"

    posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    applied_at = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("posting", "candidate")
        ordering = ["-applied_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.candidate} → {self.posting}"


class Interview(TenantModel, AuditedModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="interviews")
    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="interviews",
    )
    date = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"Interview {self.application}"


class Offer(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="offers")
    salary = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    expires_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["expires_at"]

    def __str__(self):
        return f"Offer {self.application}"
