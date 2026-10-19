from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.costing.models import CostingMethod, CostLayer, CostVariance, InventoryValuation
from apps.costing.serializers import (
    CostingMethodSerializer,
    CostLayerSerializer,
    CostVarianceSerializer,
    InventoryValuationSerializer,
)
from apps.inventory.models import StockItem


def _compute_valuations(organization):
    """Compute total inventory value per warehouse from on-hand stock × unit cost."""
    rows = {}
    for item in (
        StockItem.objects.filter(organization=organization)
        .select_related("product", "warehouse")
        .only("warehouse_id", "on_hand", "product__unit_cost")
    ):
        key = item.warehouse_id
        agg = rows.setdefault(key, {"value": Decimal("0"), "count": 0})
        agg["value"] += (item.on_hand or 0) * (item.product.unit_price or 0)
        agg["count"] += 1
    return rows


class CostingMethodViewSet(TenantViewSet):
    queryset = CostingMethod.objects.select_related("product")
    serializer_class = CostingMethodSerializer
    required_permission = "costing.view"
    write_permission = "costing.manage"
    search_fields = ["product__sku", "product__name"]
    filterset_fields = ["method", "is_active", "product"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_method = []
        for method, label in CostingMethod.Method.choices:
            subset = qs.filter(method=method)
            by_method.append({"method": method, "count": subset.count()})
        variances = CostVariance.objects.filter(organization=request.organization)
        variance_agg = variances.aggregate(total=Sum("amount"))
        latest_valuation = (
            InventoryValuation.objects.filter(organization=request.organization)
            .order_by("-date")
            .first()
        )
        return Response(
            {
                "methods": qs.count(),
                "active": qs.filter(is_active=True).count(),
                "by_method": by_method,
                "layers": CostLayer.objects.filter(
                    organization=request.organization
                ).count(),
                "variances": variances.count(),
                "variance_total": float(variance_agg["total"] or 0),
                "valuation_date": latest_valuation.date if latest_valuation else None,
                "valuation_total": float(latest_valuation.total_value or 0)
                if latest_valuation
                else 0,
            }
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        method = self.get_object()
        CostingMethod.objects.filter(
            organization=request.organization, product=method.product
        ).update(is_active=False)
        method.is_active = True
        method.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(method).data)


class CostLayerViewSet(TenantViewSet):
    queryset = CostLayer.objects.select_related("product")
    serializer_class = CostLayerSerializer
    required_permission = "costing.view"
    write_permission = "costing.manage"
    search_fields = ["product__sku", "source"]
    filterset_fields = ["product"]

    @action(detail=True, methods=["post"])
    def adjust(self, request, pk=None):
        layer = self.get_object()
        qty = Decimal(str(request.data.get("quantity", layer.quantity)))
        unit_cost = Decimal(str(request.data.get("unit_cost", layer.unit_cost)))
        layer.quantity = qty
        layer.unit_cost = unit_cost
        layer.save(update_fields=["quantity", "unit_cost", "updated_at"])
        return Response(self.get_serializer(layer).data)


class CostVarianceViewSet(TenantViewSet):
    queryset = CostVariance.objects.select_related("product")
    serializer_class = CostVarianceSerializer
    required_permission = "costing.view"
    write_permission = "costing.manage"
    search_fields = ["product__sku", "reason"]
    filterset_fields = ["product", "type"]


class InventoryValuationViewSet(TenantViewSet):
    queryset = InventoryValuation.objects.select_related("warehouse")
    serializer_class = InventoryValuationSerializer
    required_permission = "costing.view"
    write_permission = "costing.manage"
    search_fields = ["warehouse__code", "warehouse__name"]
    filterset_fields = ["warehouse", "date"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        agg = qs.aggregate(total_value=Sum("total_value"), item_count=Sum("item_count"))
        latest = qs.order_by("date").first()
        return Response(
            {
                "valuations": qs.count(),
                "warehouses": qs.values("warehouse").distinct().count(),
                "total_value": float(agg["total_value"] or 0),
                "total_items": int(agg["item_count"] or 0),
                "latest_date": latest.date if latest else None,
            }
        )

    @action(detail=False, methods=["post"])
    def recalculate(self, request):
        rows = _compute_valuations(request.organization)
        today = timezone.localdate()
        created = 0
        total = Decimal("0")
        for warehouse_id, agg in rows.items():
            total += agg["value"]
            _, was_created = InventoryValuation.objects.update_or_create(
                organization=request.organization,
                warehouse_id=warehouse_id,
                date=today,
                defaults={
                    "total_value": agg["value"],
                    "item_count": agg["count"],
                },
            )
            created += 1 if was_created else 0
        return Response(
            {
                "warehouses_valuated": len(rows),
                "created": created,
                "total_value": float(total),
                "date": today,
            }
        )
