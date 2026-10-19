from rest_framework import serializers

from apps.bills_of_materials.models import Bom, BomLine, BomRevision
from apps.core.mixins import TenantSerializer


class BomLineSerializer(TenantSerializer):
    bom_number = serializers.CharField(source="bom.product.name", read_only=True)
    component_sku = serializers.CharField(source="component.sku", read_only=True)
    component_name = serializers.CharField(source="component.name", read_only=True)

    class Meta:
        model = BomLine
        fields = (
            "id",
            "bom",
            "bom_number",
            "component",
            "component_sku",
            "component_name",
            "quantity",
            "scrap_pct",
            "uom",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class BomRevisionSerializer(TenantSerializer):
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)

    class Meta:
        model = BomRevision
        fields = (
            "id",
            "bom",
            "version",
            "notes",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class BomSerializer(TenantSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_count = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Bom
        fields = (
            "id",
            "product",
            "product_sku",
            "product_name",
            "version",
            "status",
            "effective_from",
            "effective_to",
            "notes",
            "line_count",
            "total_cost",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_line_count(self, obj):
        return obj.lines.count()

    def get_total_cost(self, obj)
        total = 0
        for line in obj.lines.select_related("component"):
            total += float(line.quantity or 0) * float(line.component.unit_cost or 0)
        return round(total, 4)
