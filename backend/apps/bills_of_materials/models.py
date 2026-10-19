from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Bom(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        OBSOLETE = "obsolete", "Obsolete"

    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="boms"
    )
    version = models.CharField(max_length=20, default="1.0")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "product", "status")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "product", "status"])]

    def __str__(self):
        return f"{self.product.sku} v{self.version}"


class BomLine(TenantModel):
    bom = models.ForeignKey(Bom, on_delete=models.CASCADE, related_name="lines")
    component = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="bom_lines"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=4)
    scrap_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    uom = models.CharField(max_length=20, default="EA")

    class Meta
        ordering = ["id"]
        indexes = [models.Index(fields=["organization", "bom"])]

    def __str__(self):
        return f"{self.bom} ← {self.component.sku} × {self.quantity}"


class BomRevision(TenantModel):
    bom = models.ForeignKey(Bom, on_delete=models.CASCADE, related_name="revisions")
    version = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_bom_revisions",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-approved_at", "-created_at"]

    def __str__(self):
        return f"{self.bom} r{self.version}"
