from django.db import models

from apps.core.models import TenantModel


class ReportJob(TenantModel)
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    name = models.CharField(max_length=160)
    report_type = models.CharField(max_length=80)
    parameters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    requested_by = models.ForeignKey(
        "accounts.User", null=True, on_delete=models.SET_NULL, related_name="report_jobs"
    )
    result = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ScorecardSnapshot(TenantModel):
    subject_type = models.CharField(max_length=40)
    subject_id = models.CharField(max_length=64)
    subject_name = models.CharField(max_length=200)
    period_start = models.DateField()
    period_end = models.DateField()
    metrics = models.JSONField(default=dict)
    composite_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
