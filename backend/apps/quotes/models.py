from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class SalesQuote(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"

    number = models.CharField(max_length=20)
    customer_ref = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    valid_until = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    currency = models.CharField(max_length=3, default="USD")

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.number


class QuoteLine(TenantModel):
    quote = models.ForeignKey(SalesQuote, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="quote_lines"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    line_total = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.quote.number} · {self.product_id}"


class QuoteRevision(TenantModel, AuditedModel):
    quote = models.ForeignKey(SalesQuote, on_delete=models.CASCADE, related_name="revisions")
    version = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    total = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    revised_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="quote_revisions",
    )

    class Meta:
        ordering = ["-version"]

    def __str__(self):
        return f"{self.quote.number} v{self.version}"


class QuoteConversion(TenantModel):
    quote = models.ForeignKey(SalesQuote, on_delete=models.CASCADE, related_name="conversions")
    sales_order_ref = models.CharField(max_length=80, blank=True)
    converted_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-converted_at"]

    def __str__(self):
        return f"{self.quote.number} → {self.sales_order_ref}"
