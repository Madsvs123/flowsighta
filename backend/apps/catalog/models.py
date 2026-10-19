from django.db import models

from apps.core.models import TenantModel


class Category(TenantModel):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = ("organization", "name")
        indexes = [models.Index(fields=["organization", "parent", "is_active"])]

    def __str__(self):
        return self.name


class Attribute(TenantModel):
    class Type(models.TextChoices):
        TEXT = "text", "Text"
        NUMBER = "number", "Number"
        SELECT = "select", "Select"
        BOOLEAN = "boolean", "Boolean"

    name = models.CharField(max_length=120)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.SELECT)
    options = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "name")

    def __str__(self):
        return self.name


class AttributeValue(TenantModel):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="values")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="attribute_values"
    )
    value = models.CharField(max_length=255)

    class Meta:
        ordering = ["attribute__name"]
        unique_together = ("organization", "attribute", "product")
        indexes = [models.Index(fields=["organization", "product", "attribute"])]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(TenantModel):
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="variants"
    )
    sku = models.CharField(max_length=64)
    attributes = models.JSONField(default=dict, blank=True)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sku"]
        unique_together = ("organization", "sku")
        indexes = [models.Index(fields=["organization", "product", "is_active"])]

    def __str__(self):
        return self.sku
