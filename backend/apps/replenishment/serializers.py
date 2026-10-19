from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.replenishment.models import (
    ReplenishmentLine,
    ReplenishmentOrder,
    ReplenishmentPolicy,
    ReplenishmentRun,
)


class ReplenishmentPolicySerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = ReplenishmentPolicy
        fields = (
            "id",
            "product",
            "sku",
            "product_name",
            "warehouse",
            "warehouse_name",
            "method",
            "min_stock",
            "max_stock",
            "lead_time_days",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ReplenishmentRunSerializer(TenantSerializer):
    line_count = serializers.SerializerMethodField()

    class Meta:
        model = ReplenishmentRun
        fields = ("id", "number", "status", "started_at", "line_count", "created_at")
        read_only_fields = ("id", "created_at")

    def get_lines_count(self, obj):
        return obj.lines.count()


class ReplenishmentLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    run_number = serializers.CharField(source="run.number", read_only=True)

    class Meta:
        model = ReplenishmentLine
        fields = (
            "id",
            "run",
            "run_number",
            "product",
            "sku",
            "product_name",
            "warehouse",
            "warehouse_name",
            "suggested_qty",
            "source",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ReplenishmentOrderSerializer(TenantSerializer):
    run_number = serializers.CharField(source="run.number", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = ReplenishmentOrder
        fields = (
            "id",
            "run",
            "run_number",
            "supplier",
            "supplier_name",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
