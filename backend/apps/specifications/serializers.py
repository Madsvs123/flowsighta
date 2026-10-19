from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.specifications.models import (
    SpecificationItem,
    SpecificationTemplate,
    SpecificationValue,
)


class SpecificationTemplateSerializer(TenantSerializer):
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SpecificationTemplate
        fields = ("id", "name", "category", "is_active", "item_count", "created_at")
        read_only_fields = ("id", "created_at")


class SpecificationItemSerializer(TenantSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)

    class Meta:
        model = SpecificationItem
        fields = (
            "id",
            "template",
            "template_name",
            "name",
            "field_type",
            "options",
            "required",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SpecificationValueSerializer(TenantSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)
    item_name = serializers.CharField(source="item.name", read_only=True)
    product_name = serializers.CharField(source="product.sku", read_only=True)
    product_sku = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = SpecificationValue
        fields = (
            "id",
            "template",
            "template_name",
            "item",
            "item_name",
            "product",
            "product_name",
            "product_sku",
            "value",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
