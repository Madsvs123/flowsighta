from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Report(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        TABULAR = "tabular", "Tabular"
        CHART = "chart", "Chart"
        PIVOT = "pivot", "Pivot"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.TABULAR)
    config = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.name


class ReportSchedule(TenantModel):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="schedules")
    cron = models.CharField(max_length=100)
    recipients = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "is_active"])]

    def __str__(self):
        return f"{self.report.name} · {self.cron}"


class ReportRun(TenantModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="runs")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    output_ref = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "report", "status"])]

    def __str__(self):
        return f"{self.report.name} · {self.status}"


class ReportTemplate(TenantModel):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=80, blank=True)
    schema = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "category"])]

    def __str__(self):
        return self.name
