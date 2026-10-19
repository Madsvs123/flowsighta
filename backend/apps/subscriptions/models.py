from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class Subscription(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    class BillingCycle(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        YEARLY = "yearly", "Yearly"

    customer_ref = models.CharField(max_length=120, blank=True)
    plan = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    billing_cycle = models.CharField(max_length=20, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    start_date = models.DateField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.plan} · {self.customer_ref}"


class SubscriptionLine(TenantModel):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="subscription_lines"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.subscription.plan} · {self.product_id}"


class SubscriptionInvoice(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="invoices")
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subscription.plan} · {self.period_start} → {self.period_end}"


class Renewal(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSED = "processed", "Processed"
        SKIPPED = "skipped", "Skipped"

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="renewals")
    renewal_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    amount = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta:
        ordering = ["renewal_date"]

    def __str__(self):
        return f"{self.subscription.plan} · {self.renewal_date}"
