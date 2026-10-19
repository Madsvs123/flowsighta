from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.receiving.models import PutawayTask, Receipt, ReceiptLine


class ReceiptSerializer(TenantSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = Receipt
        fields = (
            "id",
            "number",
            "supplier",
            "supplier_name",
            "warehouse",
            "warehouse_name",
            "reference",
            "status",
            "received_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ReceiptLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    receipt_number = serializers.CharField(source="receipt.number", read_only=True)

    class Meta:
        model = ReceiptLine
        fields = (
            "id",
            "receipt",
            "receipt_number",
            "product",
            "sku",
            "product_name",
            "quantity",
            "received_quantity",
            "batch_number",
            "expires_on",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PutawayTaskSerializer(TenantSerializer):
    receipt_number = serializers.CharField(source="receipt_line.receipt.number", read_only=True)
    sku = serializers.CharField(source="receipt_line.product.sku", read_only=True)
    bin_code = serializers.CharField(source="bin.code", read_only=True)
    assignee_name = serializers.SerializerMethodField()

    def get_assignee_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() and obj.assigned_to.email
        return ""

    class Meta:
        model = PutawayTask
        fields = (
            "id",
            "receipt_line",
            "receipt_number",
            "sku",
            "bin",
            "bin_code",
            "status",
            "assigned_to",
            "assignee_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
