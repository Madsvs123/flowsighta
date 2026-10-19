from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.transfers.models import TransferLine, TransferOrder, TransferShipment


class TransferOrderSerializer(TenantSerializer):
    from_warehouse_name = serializers.CharField(source="from_warehouse.name", read_only=True)
    from_warehouse_code = serializers.CharField(source="from_warehouse.code", read_only=True)
    to_warehouse_name = serializers.CharField(source="to_warehouse.name", read_only=True)
    to_warehouse_code = serializers.CharField(source="to_warehouse.code", read_only=True)
    requested_by_name = serializers.SerializerMethodField()

    def get_requested_by_name(self, obj):
        if obj.requested_by:
            return obj.requested_by.email or obj.requested_by.get_full_name()
         return ""

    class Meta:
        model = TransferOrder
        fields = (
            "id",
            "number",
            "from_warehouse",
            "from_warehouse_name",
            "from_warehouse_code",
            "to_warehouse",
            "to_warehouse_name",
            "to_warehouse_code",
            "status",
            "requested_by",
            "requested_by_name",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class TransferLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = TransferLine
        fields = (
            "id",
            "order",
            "order_number",
            "product",
            "sku",
            "product_name",
            "quantity",
            "shipped_quantity",
            "received_quantity",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class TransferShipmentSerializer(TenantSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)
    carrier_name = serializers.CharField(source="carrier.name", read_only=True)

    class Meta:
        model = TransferShipment
        fields = (
            "id",
            "order",
            "order_number",
            "status",
            "carrier",
            "carrier_name",
            "tracking_number",
            "shipped_at",
            "delivered_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
