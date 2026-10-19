from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class LeavePolicy(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        ANNUAL = "annual", "Annual"
        SICK = "sick", "Sick"
        MATERNITY = "maternity", "Maternity"
        UNPAID = "unpaid", "Unpaid"
        OTHER = "other", "Other"

    name = models.CharField(max_length=120)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.ANNUAL)
    days_per_year = models.PositiveIntegerField(default=0)
    carryover_days = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class LeaveBalance(TenantModel, AuditedModel):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_balances",
    )
    policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE, related_name="balances")
    year = models.PositiveIntegerField()
    allocated = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    used = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    remaining = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        unique_together = ("organization", "employee", "policy", "year")
        ordering = ["year"]

    def __str__(self):
        return f"{self.employee} · {self.policy} · {self.year}"


class LeaveRequest(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )
    policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE, related_name="requests")
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["-start_date"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.employee} · {self.policy} · {self.start_date}"


class LeaveApproval(TenantModel, AuditedModel):
    class Decision(models.TextChoices):
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name="approvals")
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_approvals",
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    comment = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-decided_at"]

    def __str__(self):
        return f"{self.request} → {self.decision}"
