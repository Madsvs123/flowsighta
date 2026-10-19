from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Portal(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        VENDOR = "vendor", "Vendor"
        PARTNER = "partner", "Partner"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.VENDOR)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "type", "status"])]

    def __str__(self):
        return self.name


class PortalMember(TenantModel):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    portal = models.ForeignKey(Portal, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portal_memberships"
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)

    class Meta:
        unique_together = ("organization", "portal")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.portal.name} · {self.user}"


class PortalContent(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    portal = models.ForeignKey(Portal, on_delete=models.CASCADE, related_name="contents")
    title = models.CharField(max_length=240)
    body = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "portal", "status"])]

    def __str__(self):
        return self.title


class PortalActivity(TenantModel):
    portal = models.ForeignKey(Portal, on_delete=models.CASCADE, related_name="activities")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="portal_activities",
    )
    action = models.CharField(max_length=120)
    details = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["organization", "portal", "occurred_at"])]

    def __str__(self):
        return f"{self.portal.name} · {self.action}"
