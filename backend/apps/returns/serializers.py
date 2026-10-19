from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.returns.models import RestockTask, ReturnLine, ReturnOrder


class ReturnOrderSerializer(TenantSerializer):
    created_by_email = serializers.CharField(source="created_by.email_address", read_only=True)
    line_count = serializers.IntegerField(read_only=True)
    total_quantity = serializers.DecimalField(max_digits=16, decimal_places=3, read_only=True)

    class Meta:
        model = ReturnOrder
        fields = (
            "id",
            "number",
            "type",
            "reference",
            "status",
            "reason",
            "created_by",
            "created_by_email",
            "line_count",
            "total_quantity",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ReturnLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = ReturnLine
        fields = (
            "id",
            "order",
            "order_number",
            "product",
            "sku",
            "product_name",
            "quantity",
            "condition",
            "disposition",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class RestockTaskSerializer(TenantSerializer):
    order_number = serializers.CharField(source="line.order.number", read_only=True)
    sku = serializers.CharField(source="line.product.sku", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = RestockTask
        fields = (
            "id",
            "line",
            "order_number",
            "sku",
            "warehouse",
            "warehouse_name",
            "bin",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
