from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.costing.models import CostingMethod, CostLayer, CostVariance, InventoryValuation


class CostingMethodSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = CostingMethod
        fields = (
            "id",
            "product",
            "sku",
            "product_name",
            "method",
            "standard_cost",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "standard_cost", "created_at")


class CostLayerSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = CostLayer
        fields = (
            "id",
            "product",
            "sku",
            "product_name",
            "quantity",
            "unit_cost",
            "source",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CostVarianceSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = CostVariance
        fields = (
            "id",
            "product",
            "sku",
            "type",
            "amount",
            "reason",
            "occurred_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class InventoryValuationSerializer(TenantSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = InventoryValuation
        fields = (
            "id",
            "warehouse",
            "warehouse_name",
            "date",
            "total_value",
            "item_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
