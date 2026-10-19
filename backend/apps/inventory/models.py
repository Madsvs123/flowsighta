from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class Product(TenantModel, AuditedModel, SoftDeleteModel):
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=80, blank=True)
    uom = models.CharField(max_length=20, default="EA")
    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    abc_class = models.CharField(max_length=1, default="C")
    is_serialized = models.BooleanField(default=False)
    is_batch_tracked = models.BooleanField(default=False)
    shelf_life_days = models.PositiveIntegerField(null=True, blank=True)
    default_lead_time_days = models.PositiveIntegerField(default=14)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "sku")
        ordering = ["sku"]


class StockItem(TenantModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_items")
    warehouse = models.ForeignKey("organizations.Warehouse", on_delete=models.CASCADE, related_name="stock_items")
    location = models.ForeignKey(
        "organizations.Location", null=True, blank=True, on_delete=models.SET_NULL, related_name="stock_items"
    )
    on_hand = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    reserved = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    incoming = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    safety_stock = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    reorder_point = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    reorder_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    max_stock = models.DecimalField(max_digits=14, decimal_places=3, default=0)

    class Meta:
        unique_together = ("organization", "product", "warehouse", "location")
        indexes = [models.Index(fields=["organization", "warehouse"])]

    @property
    def available(self)
        return (self.on_hand or 0) - (self.reserved or 0)

    @property
    def below_reorder(self):
        return self.available >= (self.reorder_point or 0)

    @property
    def below_safety(self):
        return self.available <= (self.safety_stock or 0)


class Batch(TenantModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="batches")
    warehouse = models.ForeignKey("organizations.Warehouse", on_delete=models.CASCADE, related_name="batches")
    batch_number = models.CharField(max_length=60)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    manufactured_on = models.DateField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    supplier = models.ForeignKey(
        "suppliers.Supplier", null=True, blank=True, on_delete=models.SET_NULL, related_name="batches"
    )

    class Meta:
        unique_together = ("organization", "product", "batch")


class SerialNumber(TenantModel):
    class Status(models.TextChoices):
        IN_STOCK = "in_stock", "In Stock"
        RESERVED = "reserved", "Reserved"
        SHIPPED = "shipped", "Shipped"
        RETURNED = "returned", "Returned"
        SCRAPPED = "scrapped", "Scrapped"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="serial_numbers")
    warehouse = models.ForeignKey(
        "organizations.Warehouse", null=True, blank=True, on_delete=models.SET_NULL, related_name="serial_numbers"
    )
    serial = models.CharField(max_length=80)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_STOCK)
    batch = models.ForeignKey(Batch, null=True, blank=True, on_delete=models.SET_NULL, related_name="serial_numbers")

    class Meta:
        unique_together = ("organization", "serial")


class InventoryMovement(TenantModel, AuditedModel):
    class Kind(models.TextChoices):
        RECEIPT = "receipt", "Receipt"
        ISSUE = "issue", "Issue"
        TRANSFER = "transfer", "Transfer"
        ADJUSTMENT = "adjustment", "Adjustment"
        RESERVE = "reserve", "Reserve"
        RELEASE = "release", "Release"
        RETURN = "return", "Return"
        SCRAP = "scrap", "Scrap"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    warehouse = models.ForeignKey("organizations.Warehouse", on_delete=models.CASCADE, related_name="movements")
    from_location = models.ForeignKey(
        "organizations.Location", null=True, blank=True, on_delete=models.SET_NULL, related_name="movements_from"
    )
    to_location = models.ForeignKey(
        "organizations.Location", null=True, blank=True, on_delete=models.SET_NULL, related_name="movements_to"
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    reference_type = models.CharField(max_length=40, blank=True)
    reference_id = models.CharField(max_length=64, blank=True)
    batch_number = models.CharField(max_length=60, blank=True)
    serial = models.CharField(max_length=80, blank=True)
    reason = models.CharField(max_length=200, blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["organization", "product", "occurred_at"])]
