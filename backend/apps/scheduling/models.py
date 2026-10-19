from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Schedule(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        LOCKED = "locked", "Locked"

    name = models.CharField(max_length=200)
    horizon_start = models.DateField()
    horizon_end = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.name} ({self.status})"


class ScheduleTask(TenantModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        BLOCKED = "blocked", "Blocked"

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="tasks")
    reference = models.CharField(max_length=80)
    resource = models.CharField(max_length=120, blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)

    class Meta:
        ordering = ["start_at"]
        indexes = [models.Index(fields=["organization", "schedule", "start_at"])]

    def __str__(self):
        return f"{self.reference} @ {self.resource} ({self.status})"


class ScheduleConstraint(TenantModel):
    class Type(models.TextChoices):
        RESOURCE = "resource", "Resource"
        MATERIAL = "material", "Material"
        PREDECESSOR = "predecessor", "Predecessor"
        TIME_WINDOW = "time_window", "Time Window"

    task = models.ForeignKey(ScheduleTask, on_delete=models.CASCADE, related_name="constraints")
    type = models.CharField(max_length=32, choices=Type.choices)
    value = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "task", "type"])]

    def __str__(self):
        return f"{self.type} constraint on {self.task.reference}"
