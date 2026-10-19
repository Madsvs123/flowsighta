from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class SalesOrder(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        CONFIRMED = "confirmed", "Confirmed"
        ALLOCATED = "allocated", "Allocated"
        PICKED = "picked", "Picked"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=40)
    customer_ref = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    order_date = models.DateField(null=True, blank=True)
    requested_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    tax_total = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    currency = models.CharField(max_length=3, default="USD")
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.number


class SalesOrderLine(TenantModel):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="sales_order_lines"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    allocated_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.order.number} · {self.product_id}"


class OrderAllocation(TenantModel):
    line = models.ForeignKey(SalesOrderLine, on_delete=models.CASCADE, related_name="allocations")
    stock_item = models.ForeignKey(
        "inventory.StockItem", on_delete=models.CASCADE, related_name="order_allocations"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.line_id} · {self.stock_item_id} · {self.quantity}"


class SalesShipment(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        PACKED = "packed", "Packed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"

    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="shipments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    tracking_number = models.CharField(max_length=80, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.number} · {self.status}"
