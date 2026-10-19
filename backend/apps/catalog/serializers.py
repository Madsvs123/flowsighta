from rest_framework import serializers

from apps.catalog.models import Attribute, AttributeValue, Category, ProductVariant
from apps.core.mixins import TenantSerializer


class CategorySerializer(TenantSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "parent",
            "parent_name",
            "sort_order",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class AttributeSerializer(TenantSerializer):
    class Meta:
        model = Attribute
        fields = ("id", "name", "type", "options", "created_at")
        read_only_fields = ("id", "created_at")


class AttributeValueSerializer(TenantSerializer):
    attribute_name = serializers.CharField(source="attribute.name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = AttributeValue
        fields = (
            "id",
            "attribute",
            "attribute_name",
            "product",
            "product_name",
            "product_sku",
            "value",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ProductVariantSerializer(TenantSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "product",
            "product_name",
            "product_sku",
            "sku",
            "attributes",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
