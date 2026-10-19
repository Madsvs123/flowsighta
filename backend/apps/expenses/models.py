from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class ExpenseReport(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        PAID = "paid", "Paid"
        REJECTED = "rejected", "Rejected"

    number = models.CharField(max_length=40)
    employee = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="expense_reports"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    total = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "created_at"])]

    def __str__(self):
        return f"{self.number} ({self.status}


class ExpenseLine(TenantModel):
    report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE, related_name="lines")
    category = models.CharField(max_length=80)
    date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=240, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    receipt_ref = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.report.number} - {self.category}"


class ExpenseApproval(TenantModel, AuditedModel):
    class Decision(models.TextChoices):
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE, related_name="approvals")
    approver = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="expense_approvals"
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    comment = models.TextField(blank=True)
    decided_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-decided_at"]

    def __str__(self):
        return f"{self.report.number} - {self.decision}"


class Reimbursement(TenantModel):
    report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE, related_name="reimbursements")
    payment_ref = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.report.number} - {self.payment_ref or self.amount}"
