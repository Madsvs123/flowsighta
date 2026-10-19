from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class PackingSession(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        CLOSED = "closed", "Closed"

    number = models.CharField(max_length=40)
    shipment = models.ForeignKey(
        "logistics.Shipment",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="packing_sessions",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    packed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="packing_sessions",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.number


class Box(TenantModel):
    session = models.ForeignKey(PackingSession, on_delete=models.CASCADE, related_name="boxes")
    code = models.CharField(max_length=40)
    weight = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    dims = models.JSONField(default=list, blank=True)
    is_sealed = models.BooleanField(default=False)

    class Meta:
        ordering = ["code"]
        indexes = [models.Index(fields=["organization", "session"])]

    def __str__(self):
        return f"{self.session.number} / {self.code}"


class PackedItem(TenantModel):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE, related_name="packed_items")
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    batch_number = models.CharField(max_length=60, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "box"])]

    def __str__(self):
        return f"{self.box.code} · {self.product_id}"
