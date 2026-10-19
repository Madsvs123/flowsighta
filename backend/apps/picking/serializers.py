from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.picking.models import PickLine, PickTask, PickWave


class PickWaveSerializer(TenantSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)

    class Meta:
        model = PickWave
        fields = (
            "id",
            "number",
            "warehouse",
            "warehouse_name",
            "warehouse_code",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PickLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    wave_number = serializers.CharField(source="wave.number", read_only=True)

    class Meta:
        model = PickLine
        fields = (
            "id",
            "wave",
            "wave_number",
            "product",
            "sku",
            "product_name",
            "quantity",
            "from_bin",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PickTaskSerializer(TenantSerializer):
    wave_number = serializers.CharField(source="wave.number", read_only=True)
    assignee_name = serializers.SerializerMethodField()

    def get_assignee_name(self, obj):
        if obj.assignee:
            return obj.assignee.get_full_name() or obj.assignee.email
        return ""

    class Meta:
        model = PickTask
        fields = (
            "id",
            "wave",
            "wave_number",
            "assignee",
            "assignee_name",
            "status",
            "completed_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
