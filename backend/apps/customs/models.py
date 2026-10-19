from django.db import models

from apps.core.models import AuditedModel, TenantModel


class HsCode(TenantModel, AuditedModel):
    code = models.CharField(max_length=20, db_index=True)
    description = models.CharField(max_length=240, blank=True)
    duty_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        unique_together = ("organization", "code")

    def __str__(self):
        return f"{self.code} {self.description}".strip()


class CustomsDeclaration(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        FILED = "filed", "Filed"
        CLEARED = "cleared", "Cleared"
        HELD = "held", "Held"
        REJECTED = "rejected", "Rejected"

    number = models.CharField(max_length=40)
    shipment_ref = models.CharField(max_length=80, blank=True)
    hs_code = models.ForeignKey(HsCode, null=True, blank=True, on_delete=models.SET_NULL, related_name="declarations")
    origin_country = models.CharField(max_length=80, blank=True)
    destination_country = models.CharField(max_length=80, blank=True)
    declared_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="EUR")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("organization", "number")
        indexes = [models.Index(fields=["organization", "status", "origin_country"])]

    def __str__(self):
        return f"{self.number} ({self.origin_country} → {self.destination_country})"


class CustomsDocument(TenantModel):
    declaration = models.ForeignKey(CustomsDeclaration, on_delete=models.CASCADE, related_name="documents")
    type = models.CharField(max_length=60)
    title = models.CharField(max_length=160, blank=True)
    file = models.CharField(max_length=240, blank=True)
    status = models.CharField(max_length=20, default="pending")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} {self.title}".strip()


class ComplianceRule(TenantModel):
    country = models.CharField(max_length=80, db_index=True)
    category = models.CharField(max_length=80, blank=True)
    restriction = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    effective_from = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["country", "category"]
        indexes = [models.Index(fields=["organization", "country"])]

    def __str__(self):
        return f"{self.country} / {self.category or self.restriction}"
