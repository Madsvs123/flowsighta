from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.manufacturing.models import MaterialIssue, ProductionOrder, ProductionOutput, ProductionStep


class ProductionOrderSerializer(TenantSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ProductionOrder
        fields = (
            "id",
            "number",
            "product",
            "product_sku",
            "product_name",
            "quantity",
            "status",
            "start_date",
            "due_date",
            "priority",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "number", "created_at", "updated_at")


class ProductionStepSerializer(TenantSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = ProductionStep
        fields = (
            "id",
            "order",
            "order_number",
            "sequence",
            "operation",
            "quantity",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at"


class ProductionOutputSerializer(TenantSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ProductionOutput
        fields = (
            "id",
            "order",
            "order_number",
            "product",
            "product_sku",
            "product_name",
            "quantity",
            "batch_number",
            "produced_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class MaterialIssueSerializer(TenantSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    issued_by_name = serializers.CharField(source="issued_by.get_full_name", read_only=True)

    class Meta:
        model = MaterialIssue
        fields = (
            "id",
            "order",
            "order_number",
            "product",
            "product_sku",
            "product_name",
            "quantity",
            "from_bin",
            "issued_at",
            "issued_by",
            "issued_by_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
