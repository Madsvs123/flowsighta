from django.db import models

from apps.core.models import AuditedModel, TenantModel


class WarrantyPlan(TenantModel, AuditedModel):
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="warranty_plans"
    )
    duration_months = models.PositiveIntegerField(default=24)
    coverage = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "product", "is_active"])]

    def __str__(self):
        return f"{self.product.name} · {self.duration_months} mo"


class WarrantyRegistration(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        VOID = "void", "Void"

    customer_ref = models.CharField(max_length=120, blank=True)
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="warranty_registrations"
    )
    serial = models.ForeignKey(
        "inventory.SerialNumber",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="warranty_registrations",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    class Meta:
        ordering = ["start_date"]
        indexes = [models.Index(fields=["organization", "status", "end_date"])]

    def __str__(self):
        return f"{self.customer_ref or '—'} · {self.product.name}"


class WarrantyClaim(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        UNDER_REVIEW = "under_review", "Under Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CLOSED = "closed", "Closed"

    registration = models.ForeignKey(
        WarrantyRegistration, on_delete=models.CASCADE, related_name="claims"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    date = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["organization", "status", "date"])]

    def __str__(self):
        return f"Claim on {self.registration}"


class ClaimResolution(TenantModel):
    class Type(models.TextChoices):
        REPAIR = "repair", "Repair"
        REPLACE = "replace", "Replace"
        REFUND = "refund", "Refund"
        CREDIT = "credit", "Credit"

    claim = models.ForeignKey(
        WarrantyClaim, on_delete=models.CASCADE, related_name="resolutions"
    )
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.REPAIR)
    notes = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-resolved_at"]

    def __str__(self):
        return f"{self.get_type_display()} for {self.claim}"
