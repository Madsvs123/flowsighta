from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class TransferOrder(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"
        IN_TRANSIT = "in_transit", "In Transit"
        RECEIVED = "received", "Received"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=60, blank=True)
    from_warehouse = models.ForeignKey(
        "organizations.Warehouse", on_delete=models.CASCADE, related_name="transfer_orders_out"
    )
    to_warehouse = models.ForeignKey(
        "organizations.Warehouse", on_delete=models.PROTECT, related_name="transfer_orders_in"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transfer_orders_requested",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.number or str(self.id)


class TransferLine(TenantModel):
    order = models.ForeignKey(TransferOrder, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="transfer_lines"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    shipped_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    received_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)

    class Meta:
        ordering = ["order__number", "id"]
        indexes = [models.Index(fields=["organization", "product"])]

    def __str__(self):
        return f"{self.order.number} · {self.product.sku}"


class TransferShipment(TenantModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_TRANSIT = "in_transit", "In Transit"
        DELIVERED = "delivered", "Delivered"

    order = models.ForeignKey(TransferOrder, on_delete=models.CASCADE, related_name="shipments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    carrier = models.ForeignKey(
        "logistics.Carrier",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transfer_shipments",
    )
    tracking_number = models.CharField(max_length=80, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"Shipment {self.order.number} · {self.status}"
