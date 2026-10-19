from django.db import models

from apps.core.models import AuditedModel, TenantModel


class WorkflowDefinition(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=200)
    trigger = models.CharField(max_length=120)
    config = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.name


class WorkflowInstance(TenantModel):
    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    definition = models.ForeignKey(
        WorkflowDefinition, on_delete=models.CASCADE, related_name="instances"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RUNNING, db_index=True)
    context = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "definition", "status"])]

    def __str__(self):
        return f"{self.definition.name} · {self.status}"


class WorkflowStep(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name="steps")
    name = models.CharField(max_length=160)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["organization", "instance", "status"])]

    def __str__(self):
        return f"{self.instance} · {self.name}"


class WorkflowAudit(TenantModel):
    instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name="audit_events")
    event = models.CharField(max_length=120)
    details = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["organization", "instance", "occurred_at"])]

    def __str__(self):
        return f"{self.instance} · {self.event}"
