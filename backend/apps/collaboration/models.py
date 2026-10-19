from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.models import TenantModel, TimeStampedModel


class Comment(TenantModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64)
    target = GenericForeignKey("content_type", "object_id")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    is_internal = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]


class Notification(TenantModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    category = models.CharField(max_length=40, default="system")
    severity = models.CharField(max_length=20, default="info")
    is_read = models.BooleanField(default=True)
    read_at = models.DateTimeField(null=True, blank=True)
    link = models.CharField(max_length=240, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "user", "is_read"])]


class Activity(TenantModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="activities"
    )
    verb = models.CharField(max_length=80)
    object_type = models.CharField(max_length=80)
    object_id = models.CharField(max_length=64, blank=True)
    summary = models.CharField(max_length=240)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "object_type", "created_at"])]


class Document(TenantModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64)
    target = GenericForeignKey("content_type", "object_id")
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="attachments/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="uploaded_documents"
    )
    doc_type = models.CharField(max_length=40, default="attachment")


class Task(TenantModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=20, default="medium")
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tasks"
    )
    due_date = models.DateField(null=True, blank=True)
    related_type = models.CharField(max_length=80, blank=True)
    related_id = models.CharField(max_length=64, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "due_date"]


class SavedFilter(TenantModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_filters")
    name = models.CharField(max_length=120)
    resource = models.CharField(max_length=80)
    query = models.JSONField(default=dict)
    is_shared = models.BooleanField(default=False)


class AuditLog(TenantModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs"
    )
    action = models.CharField(max_length=40)
    object_type = models.CharField(max_length=80)
    object_id = models.CharField(max_length=64, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "object_type", "created_at"])]


class SearchIndex(TimeStampedModel):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="search_index")
    object_type = models.CharField(max_length=80)
    object_id = models.CharField(max_length=64)
    title = models.CharField(max_length=240)
    subtitle = models.CharField(max_length=240, blank=True)
    keywords = models.TextField(blank=True)
    link = models.CharField(max_length=240, blank=True)

    class Meta:
        unique_together = ("organization", "object_type", "object_id")
        indexes = [models.Index(fields=["organization", "title"])]
