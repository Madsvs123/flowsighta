from django.db import models

from apps.core.models import TenantModel


class OutboundOrder(TenantModel):
    class OrderType(models.TextChoices):
        SALES = "sales", "Sales"
        TRANSFER = "transfer", "Transfer"
        RETURN = "return", "Return"

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        ALLOCATED = "allocated", "Allocated"
        PACKED = "packed", "Packed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=40)
    order_type = models.CharField(max_length=20, choices=OrderType.choices, default=OrderType.SALES)
    warehouse = models.ForeignKey(
        "organizations.Warehouse",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="outbound_orders",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, db_index=True)
    ship_to = models.JSONField(default=dict, blank=True)
    requested_ship_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.number


class OutboundLine(TenantModel):
    order = models.ForeignKey(OutboundOrder, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE, related_name="outbound_lines")
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    allocated_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    shipped_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "order"])]

    def __str__(self):
        return f"{self.order.number} · {self.product_id}"


class ShipmentPlan(TenantModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        CONFIRMED = "confirmed", "Confirmed"
        MANIFESTED = "manifested", "Manifested"

    order = models.ForeignKey(OutboundOrder, on_delete=models.CASCADE, related_name="plans")
    carrier = models.ForeignKey(
        "logistics.Carrier",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="shipment_plans",
    )
    service = models.CharField(max_length=80, blank=True)
    eta = models.DateTimeField(null=True, blank=True)
    cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.order.number} · {self.carrier_id}"
