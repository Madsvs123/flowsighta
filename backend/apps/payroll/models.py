from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class SalaryComponent(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        EARNING = "earning", "Earning"
        DEDUCTION = "deduction", "Deduction"

    name = models.CharField(max_length=120)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.DEDUCTION)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_recurring = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class PayrollRun(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PROCESSING = "processing", "Processing"
        APPROVED = "approved", "Approved"
        PAID = "paid", "Paid"

    number = models.CharField(max_length=40)
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["period_start"]

    def __str__(self):
        return self.number


class Payslip(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"
        PAID = "paid", "Paid"

    run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name="payslips")
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payslips",
    )
    gross = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        unique_together = ("organization", "run", "employee")
        ordering = ["-id"]
        indexes = [models.Index(fields=["organization", "run", "status"])]

    def __str__(self):
        return f"{self.run} · {self.employee}"


class PayrollReport(TenantModel, AuditedModel):
    run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name="reports")
    summary = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Report {self.run}"
