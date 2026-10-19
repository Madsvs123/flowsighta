from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.cycle_counts.models import CountLine, CycleCount


class CycleCountSerializer(TenantSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    counted_by_name = serializers.SerializerMethodField()

    def get_counted_by_name(self, obj):
        if obj.counted_by:
            return obj.counted_by.get_short_name() or obj.counted_by.email
        return ""

    class Meta:
        model = CycleCount
        fields = (
            "id",
            "number",
            "warehouse",
            "warehouse_name",
            "warehouse_code",
            "type",
            "status",
            "scheduled_on",
            "counted_by",
            "counted_by_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CountLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    count_number = serializers.CharField(source="count.number", read_only=True)

    class Meta:
        model = CountLine
        fields = (
            "id",
            "count",
            "count_number",
            "product",
            "sku",
            "product_name",
            "bin",
            "system_qty",
            "counted_qty",
            "variance",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
