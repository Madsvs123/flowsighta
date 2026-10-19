from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.demand_forecasting.models import (
    Forecast,
    ForecastAccuracy,
    ForecastAdjustment,
    ForecastLine,
)


class ForecastSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Forecast
        fields = (
            "id",
            "product",
            "sku",
            "product_name",
            "horizon_days",
            "method",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ForecastLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="forecast.product.sku", read_only=True)
    forecast_method = serializers.CharField(source="forecast.method", read_only=True)

    class Meta:
        model = ForecastLine
        fields = (
            "id",
            "forecast",
            "sku",
            "forecast_method",
            "period",
            "quantity",
            "confidence",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ForecastAdjustmentSerializer(TenantSerializer):
    adjusted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ForecastAdjustment
        fields = (
            "id",
            "line",
            "adjusted_quantity",
            "reason",
            "adjusted_by",
            "adjusted_by_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_adjusted_by_name(self, obj):
    return obj.adjusted_by.get_full_name() if obj.adjusted_by else None


class ForecastAccuracySerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ForecastAccuracy
        fields = (
            "id",
            "product",
            "sku",
            "product_name",
            "period",
            "forecast_qty",
            "actual_qty",
            "error_pct",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
