from django.db import models

from apps.core.models import TenantModel


class SpecificationTemplate(TenantModel):
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "name")
        indexes = [models.Index(fields=["organization", "category", "is_active"])]

    def __str__(self):
        return self.name


class SpecificationItem(TenantModel):
    class FieldType(models.TextChoices):
        TEXT = "text", "Text"
        NUMBER = "number", "Number"
        SELECT = "select", "Select"
        BOOLEAN = "boolean", "Boolean"

    template = models.ForeignKey(
        SpecificationTemplate, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=160)
    field_type = models.CharField(max_length=20, choices=FieldType.choices, default=FieldType.TEXT)
    options = models.JSONField(default=list, blank=True)
    required = models.BooleanField(default=False)

    class Meta:
        ordering = ["template__name", "name"]
        unique_together = ("organization", "template", "name")

    def __str__(self):
        return self.name


class SpecificationValue(TenantModel):
    template = models.ForeignKey(
        SpecificationTemplate, on_delete=models.CASCADE, related_name="values"
    )
    item = models.ForeignKey(SpecificationItem, on_delete=models.CASCADE, related_name="values")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="specification_values"
    )
    value = models.CharField(max_length=255)

    class Meta:
        ordering = ["product__sku", "item__name"]
        unique_together = ("organization", "item", "product")
        indexes = [models.Index(fields=["organization", "template", "product"])]

    def __str__(self):
        return f"{self.item.name}: {self.value}"
