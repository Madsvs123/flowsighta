from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Payment(TenantModel, AuditedModel):
    class Method(models.TextChoices):
        CARD = "card", "Card"
        BANK = "bank", "Bank Transfer"
        CASH = "cash", "Cash"
        CHECK = "check", "Check"
        WIRE = "wire", "Wire"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CLEARED = "cleared", "Cleared"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    reference = models.CharField(max_length=16)
    invoice_ref = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CASH)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("organization", "reference")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.reference} ({self.status})"


class PaymentTerm(TenantModel):
    name = models.CharField(max_length=120)
    days = models.PositiveIntegerField(default=0)
    discount_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["days"]

    def __str__(self):
        return self.name


class PaymentRun(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        EXECUTED = "executed", "Executed"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=32)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    executed_at = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.number} ({self.status})"


class PaymentAllocation(TenantModel):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="allocations")
    invoice_ref = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["organization", "payment"])]

    def __str__(self):
        return f"{self.payment.reference} → {self.invoice_ref}"
