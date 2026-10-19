from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantSerializer, TenantViewSet
from apps.inventory.models import Product, StockItem
from apps.planning.models import (
    DemandForecast,
    HistoricalDemand,
    InventoryProjection,
    PlanningConfig,
    PurchaseRequirement,
    ReplenishmentRecommendation,
)
from apps.suppliers.models import SupplierProduct


class PlanningConfigSerializer(TenantSerializer):
    class Meta:
        model = PlanningConfig
        fields = (
            "id",
            "horizon_weeks",
            "bucket",
            "service_level_target",
            "default_safety_stock_days",
            "auto_create_requisitions",
            "frozen_horizon_days",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class DemandForecastSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = DemandForecast
        fields = (
            "id",
            "product",
            "sku",
            "product_name",
            "warehouse",
            "period_start",
            "period_end",
            "forecast_qty",
            "actual_qty",
            "method",
            "confidence",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class HistoricalDemandSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = HistoricalDemand
        fields = ("id", "product", "sku", "warehouse", "period_start", "period_end", "quantity", "source", "created_at")
        read_only_fields = ("id", "created_at")


class InventoryProjectionSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = InventoryProjection
        fields = (
            "id",
            "product",
            "sku",
            "warehouse",
            "warehouse_name",
            "as_of",
            "starting_on_hand",
            "incoming",
            "forecast_demand",
            "projected_on_hand",
            "stockout_risk",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ReplenishmentRecommendationSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = ReplenishmentRecommendation
        fields = (
            "id",
            "product",
            "sku",
            "product_name",
            "warehouse",
            "warehouse_name",
            "supplier",
            "supplier_name",
            "recommended_qty",
            "reason",
            "needed_by",
            "projected_stockout_date",
            "status",
            "priority",
            "estimated_cost",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PurchaseRequirementSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = PurchaseRequirement
        fields = ("id", "product", "sku", "warehouse", "period_start", "quantity", "supplier", "status", "created_at")
        read_only_fields = ("id", "created_at")


def recompute_plan(organization)
    config, _ = PlanningConfig.objects.get_or_create(organization=organization)
    today = timezone.now().date()
    ReplenishmentRecommendation.objects.filter(organization=organization, status="open").delete()
    InventoryProjection.objects.filter(organization=organization).delete()
    PurchaseRequirement.objects.filter(organization=organization).delete()
    created = 0
    for stock in StockItem.objects.filter(organization=organization).select_related("product", "warehouse"):
        history = HistoricalDemand.objects.filter(organization=organization, product=stock.product).order_by("-period_start")[:8]
        avg = Decimal("0")
        if history:
            avg = sum((h.quantity for h in history), Decimal("0")) / len(history)
        weekly_demand = avg or Decimal(str(stock.reorder_quantity or 0)) / Decimal("4")
        on_hand = Decimal(str(stock.on_hand or 0))
        incoming = Decimal(str(stock.incoming or 0))
        projected = on_hand + incoming
        for week in range(config.horizon_weeks):
            start = today + timedelta(weeks=week)
            end = start + timedelta(days=7)
            DemandForecast.objects.update_or_create(
                organization=organization,
                product=stock.product,
                warehouse=stock.warehouse,
                period_start=start,
                defaults={
                    "period_end": end,
                    "forecast_qty": weekly_demand,
                    "method": "moving_average",
                    "confidence": 72,
                },
            )
            projected = projected - weekly_demand
            risk = "low"
            if projected < (stock.safety_stock or 0):
                risk = "high"
            elif projected < (stock.reorder_point or 0):
                risk = "medium"
            InventoryProjection.objects.create(
                organization=organization,
                product=stock.product,
                warehouse=stock.warehouse,
                as_of=start,
                starting_on_hand=on_hand,
                incoming=incoming if week == 0 else 0,
                forecast_demand=weekly_demand,
                projected_on_hand=projected,
                stockout_risk=risk,
            )
            if projected < 0 or (week == 0 and stock.below_reorder):
                qty = max(Decimal(str(stock.reorder_quantity or weekly_demand * 4)), weekly_demand * 2 - projected)
                supplier_product = SupplierProduct.objects.filter(
                    organization=organization, sku=stock.product.sku, is_active=True
                ).select_related("supplier").first()
                rec, was_created = ReplenishmentRecommendation.objects.get_or_create(
                    organization=organization,
                    product=stock.product,
                    warehouse=stock.warehouse,
                    status="open",
                    defaults={
                        "recommended_qty": qty,
                        "reason": "Projected coverage below reorder / safety stock",
                        "needed_by": start,
                        "priority": "low" if projected < 0 else "high",
                        "supplier": supplier_product.supplier if supplier_product else None,
                        "estimated_cost": qty * (supplier_product.unit_price if supplier_product else stock.product.unit_cost),
                    },
                )
                if was_created:
                    created += 1
                PurchaseRequirement.objects.update_or_create(
                    organization=organization,
                    product=stock.product,
                    warehouse=stock.warehouse,
                    period_start=start,
                    defaults={"quantity": qty, "supplier": rec.supplier, "status": "planned"},
                )
                break
    return created


class PlanningConfigViewSet(TenantViewSet):
    queryset = PlanningConfig.objects.all()
    serializer_class = PlanningConfigSerializer
    required_permission = "planning.view"
    write_permission = "planning.manage"
    http_method_names = ["get", "put", "patch", "head", "options"]

    def list(self, request):
        config, _ = PlanningConfig.objects.get_or_create(organization=request.organization)
        return Response(self.get_serializer(config).data)


class DemandForecastViewSet(TenantViewSet):
    queryset = DemandForecast.objects.select_related("product", "warehouse")
    serializer_class = DemandForecastSerializer
    required_permission = "planning.view"
    write_permission = "planning.manage"
    filterset_fields = ["product", "warehouse"]
    search_fields = ["product__sku", "product__name"]


class HistoricalDemandViewSet(TenantViewSet):
    queryset = HistoricalDemand.objects.select_related("product")
    serializer_class = HistoricalDemandSerializer
    required_permission = "planning.view"
    write_permission = "planning.manage"
    filterset_fields = ["product", "warehouse"]


class InventoryProjectionViewSet(TenantViewSet):
    queryset = InventoryProjection.objects.select_related("product", "warehouse")
    serializer_class = InventoryProjectionSerializer
    required_permission = "planning.view"
    write_permission = "planning.manage"
    http_method_names = ["get", "head", "options"]
    filterset_fields = ["product", "warehouse", "stockout_risk"]


class ReplenishmentRecommendationViewSet(TenantViewSet):
    queryset = ReplenishmentRecommendation.objects.select_related("product", "warehouse", "supplier")
    serializer_class = ReplenishmentRecommendationSerializer
    required_permission = "planning.view"
    write_permission = "planning.manage"
    filterset_fields = ["status", "priority", "warehouse", "supplier"]

    @action(detail=False, methods=["post"])
    def recompute(self, request):
        created = recompute_plan(request.organization)
        return Response({"created": created})

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        rec = self.get_object()
        rec.status = ReplenishmentRecommendation.Status.CONVERTED
        rec.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(rec).data)


class PurchaseRequirementViewSet(TenantViewSet):
    queryset = PurchaseRequirement.objects.select_related("product", "warehouse")
    serializer_class = PurchaseRequirementSerializer
    required_permission = "planning.view"
    write_permission = "planning.manage"
    filterset_fields = ["warehouse", "status", "product"]


@shared_task
def recompute_active_plans():
    from apps.organizations.models import Organization

    total = 0
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        total += recompute_plan(org)
    return {"recommendations": total}
