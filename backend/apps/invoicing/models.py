from django.db import models

from apps.core.models import AuditedModel, TenantModel


class CustomerInvoice(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PARTIAL = "partial", "Partial"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        VOID = "void", "Void"

    number = models.CharField(max_length=32)
    customer_ref = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    issue_date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="USD")

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-issue_date", "-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.number} ({self.status})"


class InvoiceLine(TenantModel):
    invoice = models.ForeignKey(CustomerInvoice, on_delete=models.CASCADE, related_name="line")
    description = models.CharField(max_length=240)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=1)
    rate = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    tax_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["organization", "invoice"])]

    def __str__(self):
        return f"{self.invoice.number} · {self.description}"


class CreditNote(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        APPLIED = "applied", "Applied"

    invoice = models.ForeignKey(CustomerInvoice, on_delete=models.CASCADE, related_name="credit_notes")
    number = models.CharField(max_length=32)
    reason = models.CharField(max_length=240, blank=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.number} ({self.status})"
