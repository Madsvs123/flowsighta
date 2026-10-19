from django.db.models import Avg, Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.demand_forecasting.models import (
    Forecast,
    ForecastAccuracy,
    ForecastAdjustment,
    ForecastLine,
)
from apps.demand_forecasting.serializers import (
    ForecastAccuracySerializer,
    ForecastAdjustmentSerializer,
    ForecastLineSerializer,
    ForecastSerializer,
)
from apps.demand_forecasting.tasks import generate_forecast_lines


class ForecastViewSet(TenantViewSet):
    queryset = Forecast.objects.select_related("product")
    serializer_class = ForecastSerializer
    required_permission = "demand_forecasting.view"
    write_permission = "demand_forecasting.manage"
    search_fields = ["product__sku", "product__name"]
    filterset_fields = ["product", "method", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        lines = ForecastLine.objects.filter(organization=request.organization)
        return Response(
            {
                "total": qs.count(),
                "draft": qs.filter(status=Forecast.Status.DRAFT).count(),
                "published": qs.filter(status=Forecast.Status.PUBLISHED).count(),
                "archived": qs.filter(status=Forecast.Status.ARCHIVED).count(),
                "products_covered": qs.values("product").count(),
                "line_count": lines.count(),
                "total_quantity": float(lines.aggregate(s=Sum("quantity"))["s"] or 0),
                "avg_confidence": float(lines.aggregate(a=Sum("confidence"))["a"] or 0),
            }
        )

    @action(detail=False, methods=["post"])
    def generate(self, request):
        result = generate_forecast_lines(organization_id=request.organization.id)
        return Response(result)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        forecast = self.get_object()
        forecast.status = Forecast.Status.PUBLISHED
        forecast.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(forecast).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        forecast = self.get_object()
        forecast.status = Forecast.Status.ARCHIVED
        forecast.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(forecast).data)


class ForecastLineViewSet(TenantViewSet):
    queryset = ForecastLine.objects.select_related("forecast", "forecast__product")
    serializer_class = ForecastLineSerializer
    required_permission = "demand_forecasting.view"
    write_permission = "demand_forecasting.manage"
    search_fields = ["forecast__product__sku"]
    filterset_fields = ["forecast", "period"]


class ForecastAdjustmentViewSet(TenantViewSet):
    queryset = ForecastAdjustment.objects.select_related("line", "adjusted_by")
    serializer_class = ForecastAdjustmentSerializer
    required_permission = "demand_forecasting.view"
    write_permission = "demand_forecasting.manage"
    search_fields = ["reason"]
    filterset_fields = ["line", "adjusted_by"]


class ForecastAccuracyViewSet(TenantViewSet):
    queryset = ForecastAccuracy.objects.select_related("product")
    serializer_class = ForecastAccuracySerializer
    required_permission = "demand_forecasting.view"
    write_permission = "demand_forecasting.manage"
    search_fields = ["product__sku"]
    filterset_fields = ["product", "period"]
