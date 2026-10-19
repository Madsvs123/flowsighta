from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class Document(TenantModel):
    class Type(models.TextChoices):
        POLICY = "policy", "Policy"
        PROCEDURE = "procedure", "Procedure"
        SPEC = "spec", "Specification"
        CERT = "cert", "Certificate"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_REVIEW = "in_review", "In Review"
        APPROVED = "approved", "Approved"
        OBSOLETE = "obsolete", "Obsolete"

    code = models.CharField(max_length=40)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.POLICY)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.APPROVED, db_index=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_documents",
    )

    class Meta:
        ordering = ["code"]
        unique_together = ("organization", "code")
        indexes = [models.Index(fields=["organization", "type", "status"])]

    def __str__(self):
        return f"{self.code} — {self.title}"


class DocumentRevision(TenantModel):
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="revisions"
    )
    version = models.CharField(max_length=20)
    file = models.FileField(upload_to="documents/", blank=True)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_document_revisions",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-version"]
        unique_together = ("organization", "document", "version")
        indexes = [models.Index(fields=["organization", "document", "approved_at"])]

    def __str__(self):
        return f"{self.document.code} v{self.version}"


class DocumentApproval(TenantModel):
    class Decision(models.TextChoices):
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    revision = models.ForeignKey(
        DocumentRevision, on_delete=models.CASCADE, related_name="approvals"
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="document_approvals",
    )
    decision = models.CharField(
        max_length=20, choices=Decision.choices, default=Decision.APPROVED
    )
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("organization", "revision", "approver")
        indexes = [models.Index(fields=["organization", "revision", "decision"])]

    def __str__(self):
        return f"{self.revision} — {self.get_decision_display()} by {self.approver}"


class DocumentLink(TenantModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="links")
    object_type = models.CharField(max_length=80)
    object_id = models.CharField(max_length=64)

    class Meta:
        ordering = ["object_type", "object_id"]
        unique_together = ("organization", "document", "object_type", "object_id")

    def __str__(self):
        return f"{self.document.code} → {self.object_type}:{self.object_id}"
