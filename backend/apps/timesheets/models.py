from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Timesheet(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="timesheets")
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ["-period_start"]
        unique_together = ("organization", "user", "period_start", "period_end")
        indexes = [models.Index(fields=["organization", "user", "status"])]

    def __str__(self):
        return f"{self.user} / {self.period_start} - {self.period_end}"


class TimesheetEntry(TenantModel):
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name="entries")
    date = models.DateField()
    project_ref = models.CharField(max_length=64, blank=True)
    activity = models.CharField(max_length=200, blank=True)
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["date"]
        indexes = [models.Index(fields=["organization", "timesheet", "date"])]

    def __str__(self):
        return f"{self.timesheet} / {self.date}"


class TimesheetApproval(TenantModel):
    class Decision(models.TextChoices):
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name="approvals")
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="timesheet_approvals",
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    comment = models.TextField(blank=True)
    decided_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-decided_at"]

    def __str__(self):
        return f"{self.timesheet} / {self.decision}"


class TimesheetPolicy(TenantModel):
    name = models.CharField(max_length=120)
    hours_per_day = models.DecimalField(max_digits=6, decimal_places=2, default=8)
    overtime_rule = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "name")

    def __str__(self):
        return self.name
