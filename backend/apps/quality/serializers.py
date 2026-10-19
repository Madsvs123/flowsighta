from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.quality.models import (
    CorrectiveAction,
    InspectionResult,
    NonConformance,
    QualityInspection,
    QualityPlan,
)


class QualityPlanSerializer(TenantSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = QualityPlan
        fields = (
            "id",
            "product",
            "product_sku",
            "product_name",
            "name",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class InspectionResultSerializer(TenantSerializer):
    inspection_reference = serializers.CharField(source="inspection.reference", read_only=True)

    class Meta:
        model = InspectionResult
        fields = (
            "id",
            "inspection",
            "inspection_reference",
            "attribute",
            "value",
            "limit_min",
            "limit_max",
            "passed",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class QualityInspectionSerializer(TenantSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    product_sku = serializers.CharField(source="plan.product.sku", read_only=True)
    inspected_by_name = serializers.CharField(source="inspected_by.get_full_name", read_only=True)
    result_count = serializers.SerializerMethodField()
    passed_count = serializers.SerializerMethodField()

    class Meta:
        model = QualityInspection
        fields = (
            "id",
            "plan",
            "plan_name",
            "product_sku",
            "reference",
            "status",
            "inspected_by",
            "inspected_by_name",
            "inspected_at",
            "result_count",
            "passed_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_result_count(self, obj):
        return obj.results.count()

    def get_passed_count(self, obj):
        return obj.results.filter(passed=False).count(


class NonConformanceSerializer(TenantSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    corrective_action_count = serializers.SerializerMethodField()

    class Meta:
        model = NonConformance
        fields = (
            "id",
            "reference",
            "product",
            "product_sku",
            "product_name",
            "type",
            "severity",
            "status",
            "description",
            "disposition",
            "corrective_action_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_corrective_action_count(self, obj):
        return obj.corrective_actions.count()


class CorrectiveActionSerializer(TenantSerializer):
    nc_reference = serializers.CharField(source="nc.reference", read_only=True)
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)

    class Meta:
        model = CorrectiveAction
        fields = (
            "id",
            "nc",
            "nc_reference",
            "action",
            "owner",
            "owner_name",
            "due_date",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
