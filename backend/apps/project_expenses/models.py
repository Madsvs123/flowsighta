from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class ProjectExpense(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    project_ref = models.CharField(max_length=64)
    category = models.CharField(max_length=80, blank=True)
    date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    vendor_ref = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [models.Index(fields=["organization", "project_ref", "status"])]

    def __str__(self):
        return f"{self.project_ref} / {self.description or self.category}"


class ExpenseBudget(TenantModel):
    project_ref = models.CharField(max_length=64)
    category = models.CharField(max_length=80, blank=True)
    planned_amount = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        ordering = ["project_ref", "category"]
        unique_together = ("organization", "project_ref", "category")

    def __str__(self):
        return f"{self.project_ref} / {self.category}"


class ExpenseApproval(TenantModel):
    class Decision(models.TextChoices):
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    expense = models.ForeignKey(ProjectExpense, on_delete=models.PROTECT, related_name="approvals")
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="expense_approvals",
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    comment = models.TextField(blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-decided_at"]

    def __str__(self):
        return f"{self.expense} / {self.decision}"


class ProjectBilling(TenantModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"

    project_ref = models.CharField(max_length=64)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    billing_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["-billing_date"]
        indexes = [models.Index(fields=["organization", "project_ref", "status"])]

    def __str__(self):
        return f"{self.project_ref} / {self.billing_date}"
