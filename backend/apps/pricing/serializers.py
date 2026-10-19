from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.pricing.models import Discount, PriceChange, PriceList, PriceListItem


class PriceListSerializer(TenantSerializer):
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PriceList
        fields = (
            "id",
            "name",
            "currency",
            "is_default",
            "status",
            "item_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PriceListItemSerializer(TenantSerializer):
    price_list_name = serializers.CharField(source="price_list.currency", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = PriceListItem
        fields = (
            "id",
            "price_list",
            "price_list_name",
            "product",
            "product_name",
            "product_sku",
            "price",
            "min_quantity",
            "effective_from",
            "effective_to",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class DiscountSerializer(TenantSerializer):
    class Meta:
        model = Discount
        fields = (
            "id",
            "name",
            "type",
            "value",
            "status",
            "valid_from",
            "valid_to",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PriceChangeSerializer(TenantSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    changed_by_email = serializers.CharField(source="changed_by.email", read_only=True)

    class Meta:
        model = PriceChange
        fields = (
            "id",
            "product",
            "product_name",
            "product_sku",
            "old_price",
            "new_price",
            "reason",
            "changed_by",
            "changed_by_email",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
