from django.db import models

from apps.core.models import TenantModel


class CostingMethod(TenantModel):
    class Method(models.TextChoices):
        FIFO = "fifo", "FIFO"
        LIFO = "lifo", "LIFO"
        AVERAGE = "average", "Average"
        STANDARD = "standard", "Standard"

    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="costing_methods"
    )
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.AVERAGE)
    standard_cost = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "product", "method")
        ordering = ["product__sku"]
        indexes = [models.Index(fields=["organization", "is_active"])]

    def __str__(self):
        return f"{self.product.sku} · {self.method}"


class CostLayer(TenantModel):
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="cost_layers"
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    unit_cost = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    source = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "product"])]

    def __str__(self):
        return f"{self.product.sku} · {self.unit_cost}"


class CostVariance(TenantModel):
    class Type(models.TextChoices):
        PRICE = "price", "Price"
        QUANTITY = "quantity", "Quantity"
        METHOD = "method", "Method"

    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="cost_variances"
    )
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.PRICE)
    amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    reason = models.CharField(max_length=240, blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["organization", "product", "occurred_at"])]

    def __str__(self):
        return f"{self.product.sku} · {self.type} · {self.amount}"


class InventoryValuation(TenantModel):
    warehouse = models.ForeignKey(
        "organizations.Warehouse", on_delete=models.CASCADE, related_name="valuations"
    )
    date = models.DateField()
    total_value = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    item_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("organization", "warehouse", "date")
        ordering = ["-date"]
        indexes = [models.Index(fields=["organization", "date"])]

    def __str__(self):
        return f"{self.warehouse.code} @ {self.date}"
