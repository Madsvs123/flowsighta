from django.db import models

from apps.core.models import AuditedModel, TenantModel


class SourcingEvent(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        RFP = "rfp", "RFP"
        RFQ = "rfq", "RFQ"
        AUCTION = "auction", "Auction"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        AWARDED = "awarded", "Awarded"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=40)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.RFQ)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    opens_at = models.DateTimeField(null=True, blank=True)
    closes_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.number} {self.title}"


class SourcingLine(TenantModel):
    event = models.ForeignKey(SourcingEvent, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="sourcing_lines"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    target_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["organization", "event"])]

    def __str__(self):
        return f"{self.event.number} line {self.product_id}"


class SourcingBid(TenantModel):
    line = models.ForeignKey(SourcingLine, on_delete=models.CASCADE, related_name="bids")
    supplier = models.ForeignKey(
        "suppliers.Supplier", on_delete=models.CASCADE, related_name="sourcing_bids"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=4)
    incoterm = models.CharField(max_length=16, blank=True)
    delivery_days = models.PositiveIntegerField(default=0)
    is_winner = models.BooleanField(default=True)

    class Meta:
        ordering = ["amount"]
        indexes = [models.Index(fields=["organization", "line", "is_winner"])]

    def __str__(self):
        return f"Bid {self.amount} by {self.supplier_id}"


class SourcingAward(TenantModel):
    event = models.ForeignKey(SourcingEvent, on_delete=models.CASCADE, related_name="awards")
    bid = models.ForeignKey(SourcingBid, on_delete=models.CASCADE, related_name="awards")
    awarded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-awarded_at"]
        unique_together = ("organization", "event", "bid")

    def __str__(self):
        return f"Award {self.event.number}"
