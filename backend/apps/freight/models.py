from django.db import models

from apps.core.models import AuditedModel, TenantModel


class FreightQuote(TenantModel, AuditedModel):
    class Mode(models.TextChoices):
        LTL = "ltl", "LTL"
        FTL = "ftl", "FTL"
        AIR = "air", "Air"
        OCEAN = "ocean", "Ocean"
        PARCEL = "parcel", "Parcel"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"

    carrier = models.ForeignKey(
        "logistics.Carrier", on_delete=models.CASCADE, related_name="freight_quotes"
    )
    origin = models.CharField(max_length=160)
    destination = models.CharField(max_length=160)
    mode = models.CharField(max_length=16, choices=Mode.choices, default=Mode.LTL, db_index=True)
    rate = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    transit_days = models.PositiveIntegerField(default=1)
    valid_until = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "mode"])]

    def __str__(self):
        return f"{self.carrier.name} {self.origin} → {self.destination}"


class FreightBooking(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        CONFIRMED = "confirmed", "Confirmed"
        BOOKED = "booked", "Booked"
        CANCELLED = "cancelled", "Cancelled"

    quote = models.ForeignKey(FreightQuote, on_delete=models.CASCADE, related_name="bookings")
    reference = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)
    booked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.reference or f"Booking #{self.pk}"


class FreightBill(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        PAID = "paid", "Paid"
        DISPUTED = "disputed", "Disputed"

    booking = models.ForeignKey(FreightBooking, on_delete=models.CASCADE, related_name="bills")
    number = models.CharField(max_length=60)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("organization", "reference")
        indexes = [models.Index(fields=["organization", "status", "due_date"])]

    def __str__(self):
        return f"{self.number} ({self.booking})"


class AccessorialCharge(TenantModel):
    booking = models.ForeignKey(FreightBooking, on_delete=models.CASCADE, related_name="accessorials")
    type = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} @ {self.amount}"
