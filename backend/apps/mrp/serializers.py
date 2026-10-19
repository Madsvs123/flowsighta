from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.mrp.models import MrpException, MrpRequirement, MrpRun


class MrpRunSerializer(TenantSerializer):
    class Meta:
        model = MrpRun
        fields = (
            "id",
            "number",
            "status",
            "horizon_days",
            "started_at",
            "finished_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class MrpRequirementSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    run_number = serializers.CharField(source="run.number", read_only=True)

    class Meta:
        model = MrpRequirement
        fields = (
            "id",
            "run",
            "run_number",
            "product",
            "sku",
            "product_name",
            "gross_requirement",
            "scheduled_receipts",
            "projected_balance",
            "net_requirement",
            "planned_order_qty",
            "planned_order_date",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class MrpExceptionSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    run_number = serializers.CharField(source="run.number", read_only=True)

    class Meta:
        model = MrpException
        fields = ("id", "run", "run_number", "product", "sku", "type", "notes", "created_at")
        read_only_fields = ("id", "created_at")
