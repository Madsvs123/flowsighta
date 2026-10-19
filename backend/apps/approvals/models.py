from django.db import models

from apps.core.models import AuditedModel, TenantModel


class ApprovalPolicy(TenantModel, AuditedModel):
    name = models.CharField(max_length=200)
    object_type = models.CharField(max_length=80)
    conditions = models.JSONField(default=dict, blank=True)
    threshold = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ApprovalRequest(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    policy = models.ForeignKey(ApprovalPolicy, on_delete=models.PROTECT, related_name="requests")
    reference = models.CharField(max_length=120)
    object_id = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPROVED, db_index=True)
    requested_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="approval_requests"
    )
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-requested_at"]
        indexes = [models.Index(fields=["organization", "status", "requested_at"])]

    def __str__(self):
        return f"{self.reference} ({self.status})"


class ApprovalStep(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SKIPPED = "skipped", "Skipped"

    request = models.ForeignKey(ApprovalRequest, on_delete=models.CASCADE, related_name="steps")
    approver = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="approval_steps"
    )
    sequence = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ["sequence"]
        unique_together = ("organization", "request", "sequence")

    def __str__(self):
        return f"{self.request.reference} step {self.sequence}"


class ApprovalDecision(TenantModel, AuditedModel):
    class Decision(models.TextChoices):
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    step = models.ForeignKey(ApprovalStep, on_delete=models.CASCADE, related_name="decisions")
    decision = models.CharField(max_length=20, choices=Decision.choices)
    comment = models.TextField(blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-decided_at"]

    def __str__(self):
        return f"{self.step} -> {self.decision}"
