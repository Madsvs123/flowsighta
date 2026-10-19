from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.sales_orders.models import OrderAllocation, SalesOrder, SalesOrderLine, SalesShipment


class SalesOrderSerializer(TenantSerializer):
    class Meta:
        model = SalesOrder
        fields = (
            "id",
            "number",
            "customer_ref",
            "status",
            "order_date",
            "requested_date",
            "subtotal",
            "tax_total",
            "total",
            "currency",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SalesOrderLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = SalesOrderLine
        fields = (
            "id",
            "order",
            "order_number",
            "product",
            "sku",
            "product_name",
            "quantity",
            "allocated_quantity",
            "unit_price",
            "line_total",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class OrderAllocationSerializer(TenantSerializer):
    sku = serializers.CharField(source="stock_item.product.sku", read_only=True)
    order_number = serializers.CharField(source="line.order.number", read_only=True)

    class Meta:
        model = OrderAllocation
        fields = (
            "id",
            "line",
            "order_number",
            "stock_item",
            "sku",
            "quantity",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SalesShipmentSerializer(TenantSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = SalesShipment
        fields = (
            "id",
            "order",
            "order_number",
            "status",
            "tracking_number",
            "shipped_at",
            "created_at",
        )
        read_only_fields = ("id", "shipped_at", "created_at")
