from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.shipping.models import OutboundLine, OutboundOrder, ShipmentPlan


class OutboundOrderSerializer(TenantSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    line_count = serializers.IntegerField(read_only=True)
    total_quantity = serializers.DecimalField(max_digits=16, decimal_places=3, read_only=True)

    class Meta:
        model = OutboundOrder
        fields = (
            "id",
            "number",
            "order_type",
            "warehouse",
            "warehouse_name",
            "status",
            "ship_to",
            "requested_ship_date",
            "line_count",
            "total_quantity",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class OutboundLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = OutboundLine
        fields = (
            "id",
            "order",
            "order_number",
            "product",
            "sku",
            "product_name",
            "quantity",
            "allocated_quantity",
            "shipped_quantity",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ShipmentPlanSerializer(TenantSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)
    carrier_name = serializers.CharField(source="carrier.name", read_only=True)

    class Meta:
        model = ShipmentPlan
        fields = (
            "id",
            "order",
            "order_number",
            "carrier",
            "carrier_name",
            "service",
            "eta",
            "cost",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "status")
