from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class PortalUser(TenantModel, AuditedModel):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        USER = "user", "User"
        VIEWER = "viewer", "Viewer"

    supplier = models.ForeignKey(
        "suppliers.Supplier", on_delete=models.CASCADE, related_name="portal_users"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendor_portal_users"
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["supplier__name", "user__email"]
        unique_together = ("organization", "supplier", "user")
        indexes = [models.Index(fields=["organization", "supplier", "is_active"])]

    def __str__(self):
        return f"{self.supplier.name} · {self.user.email}"


class PortalDocument(TenantModel):
    class Type(models.TextChoices):
        CERT = "cert", "Certification"
        INSURANCE = "insurance", "Insurance"
        CONTRACT = "contract", "Contract"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    supplier = models.ForeignKey(
        "suppliers.Supplier", on_delete=models.CASCADE, related_name="portal_documents"
    )
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.OTHER)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="vendor-portal/documents/", blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [models.Index(fields=["organization", "supplier", "status"])]

    def __str__(self):
        return f"{self.supplier.name} · {self.title}"


class PortalMessage(TenantModel, AuditedModel):
    class Direction(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND = "outbound", "Outbound"

    supplier = models.ForeignKey(
        "suppliers.Supplier", on_delete=models.CASCADE, related_name="portal_messages"
    )
    subject = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    direction = models.CharField(max_length=20, choices=Direction.choices, default=Direction.INBOUND)
    is_read = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "supplier", "is_read"])]

    def __str__(self):
        return f"{self.supplier.name} · {self.subject}"
