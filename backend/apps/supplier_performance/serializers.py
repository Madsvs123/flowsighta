from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.supplier_performance.models import PerformanceScorecard, ScorecardMetric


class PerformanceScorecardSerializer(TenantSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    supplier_code = serializers.CharField(source="supplier.name", read_only=True)
    metric_count = serializers.IntegerField(source="metrics.count", read_only=True)

    class Meta:
        model = PerformanceScorecard
        fields = (
            "id",
            "supplier",
            "supplier_name",
            "supplier_code",
            "period",
            "on_time_delivery_rate",
            "fill_rate",
            "quality_rate",
            "cost_index",
            "composite_score",
            "status",
            "metric_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ScorecardMetricSerializer(TenantSerializer):
    scorecard_period = serializers.CharField(source="scorecard.period", read_only=True)
    supplier_name = serializers.CharField(source="scorecard.supplier.name", read_only=True)

    class Meta:
        model = ScorecardMetric
        fields = (
            "id",
            "scorecard",
            "scorecard_period",
            "supplier_name",
            "metric",
            "target",
            "actual",
            "weight",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
