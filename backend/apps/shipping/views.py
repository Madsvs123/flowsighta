from django.db.models import Count, Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.shipping.models import OutboundLine, OutboundOrder, ShipmentPlan
from apps.shipping.serializers import OutboundLineSerializer, OutboundOrderSerializer, ShipmentPlanSerializer


class OutboundOrderViewSet(TenantViewSet):
    queryset = OutboundOrder.objects.select_related("warehouse").annotate(
        line_count=Count("lines"),
        total_quantity=Sum("lines__quantity"),
    )
    serializer_class = OutboundOrderSerializer
    required_permission = "shipping.view"
    write_permission = "shipping.manage"
    search_fields = ["number", "warehouse__name", "warehouse__code"]
    filterset_fields = ["status", "order_type", "warehouse"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        lines = OutboundLine.objects.filter(organization=request.organization)
        plans = ShipmentPlan.objects.filter(organization=request.organization)
        return Response(
            {
                "orders": qs.count(),
                "open": qs.exclude(
                    status__in=[
                        OutboundOrder.Status.SHIPPED,
                        OutboundOrder.Status.DELIVERED,
                        OutboundOrder.Status.CANCELLED,
                    ]
                ).count(),
                "shipped": qs.filter(status=OutboundOrder.Status.SHIPPED).count(),
                "delivered": qs.filter(status=OutboundOrder.Status.DELIVERED).count(),
                "cancelled": qs.filter(status=OutboundOrder.Status.CANCELLED).count(),
                "units_ordered": float(lines.aggregate(total=Sum("quantity"))["total"] or 0),
                "units_allocated": float(lines.aggregate(total=Sum("allocated_quantity"))["total"] or 0),
                "units_shipped": float(lines.aggregate(total=Sum("shipped_quantity"))["total"] or 0),
                "plans": plans.count(),
                "manifested": plans.filter(status=ShipmentPlan.Status.MANIFESTED).count(),
                "plan_cost": float(plans.aggregate(total=Sum("cost"))["total"] or 0),
            }
        )

    @action(detail=True, methods=["post"])
    def ship(self, request, pk=None):
        order = self.get_object()
        order.status = OutboundOrder.Status.DELIVERED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def deliver(self, request, pk=None):
         order = self.get_object()
        order.status = OutboundOrder.Status.DELIVERED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)


class OutboundLineViewSet(TenantViewSet):
    queryset = OutboundLine.objects.select_related("order", "product")
    serializer_class = OutboundLineSerializer
    required_permission = "shipping.view"
    write_permission = "shipping.manage"
    search_fields = ["order__number", "product__sku"]
    filterset_fields = ["order", "product"]


class ShipmentPlanViewSet(TenantViewSet):
    queryset = ShipmentPlan.objects.select_related("order", "carrier")
    serializer_class = ShipmentPlanSerializer
    required_permission = "shipping.view"
    write_permission = "shipping.manage"
    search_fields = ["order__number", "carrier__name", "service"]
    filterset_fields = ["status", "order", "carrier"]

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        plan = self.get_object()
        plan.status = ShipmentPlan.Status.CONFIRMED
        plan.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(plan).data)

    @action(detail=True, methods=["post"])
    def manifest(self, request, pk=None):
        plan = self.get_object()
        plan.status = ShipmentPlan.Status.MANIFESTED
        plan.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(plan).data)
