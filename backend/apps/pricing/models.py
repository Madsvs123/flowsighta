from django.db import models

from apps.core.models import TenantModel


class PriceList(TenantModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=160)
    currency = models.CharField(max_length=8, default="usd")
    is_default = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "name")

    def __str__(self):
        return self.name


class PriceListItem(TenantModel):
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="price_list_items"
    )
    price = models.DecimalField(max_digits=14, decimal_places=4)
    min_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["price_list__name", "product__sku"]
        unique_together = ("organization", "price_list", "product")
        indexes = [models.Index(fields=["organization", "price_list", "product"])]

    def __str__(self):
        return f"{self.price_list.name} / {self.product.sku}"


class Discount(TenantModel):
    class Type(models.TextChoices):
        PERCENT = "percent", "Percent"
        FIXED = "fixed", "Fixed"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        EXPIRED = "expired", "Expired"

    name = models.CharField(max_length=160)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.PERCENT)
    value = models.DecimalField(max_digits=14, decimal_places=4)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.name


class PriceChange(TenantModel):
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="price_changes"
    )
    old_price = models.DecimalField(max_digits=14, decimal_places=4)
    new_price = models.DecimalField(max_digits=14, decimal_places=4)
    reason = models.CharField(max_length=200, blank=True)
    changed_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="price_changes"
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "product", "-created_at"])]

    def __str__(self):
        return f"{self.product.sku}: {self.old_price} -> {self.new_price}"
