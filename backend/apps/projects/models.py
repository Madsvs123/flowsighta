from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Project(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    code = models.CharField(max_length=32)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNING)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_projects",
    )
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["code"]
        unique_together = ("organization", "code")
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProjectMember(TenantModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_memberships"
    )
    role = models.CharField(max_length=60, blank=True)

    class Meta:
        ordering = ["project__code"]
        unique_together = ("organization", "project", "user")

    def __str__(self):
        return f"{self.project.code} / {self.user}"


class ProjectTask(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        BLOCKED = "blocked", "Blocked"

    class Priority(models.TextChoices)
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="project_tasks",
    )
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)

    class Meta:
        ordering = ["due_date", "-priority"]
        indexes = [models.Index(fields=["organization", "project", "status"])]

    def __str__(self):
        return self.title


class ProjectMilestone(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACHIEVED = "achieved", "Achieved"
        SLIPPED = "slipped", "Slipped"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=200)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["date"]
        indexes = [models.Index(fields=["organization", "project", "status"])]

    def __str__(self):
        return f"{self.project.code} / {self.title}"
