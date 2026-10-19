from django.db import models

from apps.core.models import TenantModel


class TaxCode(TenantModel):
    code = models.CharField(max_length=24)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["code"]
        unique_together = ("organization", "code")

    def __str__(self):
        return f"{self.code} {self.name}"


class TaxRate(TenantModel):
    tax_code = models.ForeignKey(TaxCode, on_delete=models.CASCADE, related_name="rates")
    jurisdiction = models.CharField(max_length=120)
    rate = models.DecimalField(max_digits=8, decimal_places=4)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["jurisdiction", "tax_code__code"]
        unique_together = ("organization", "tax_code", "jurisdiction", "effective_from")
        indexes = [models.Index(fields=["organization", "tax_code", "is_active"])]

    def __str__(self):
        return f"{self.tax_code.code} {self.jurisdiction} {self.rate}"


class TaxRule(TenantModel):
    name = models.CharField(max_length=160)
    product = models.ForeignKey(
        "inventory.Product", null=True, blank=True, on_delete=models.SET_NULL, related_name="tax_rules"
    )
    category = models.CharField(max_length=80, blank=True)
    tax_code = models.ForeignKey(TaxCode, on_delete=models.CASCADE, related_name="rules")
    applies_from = models.DateField(null=True, blank=True)
    applies_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "category"])]

    def __str__(self):
        return self.name
