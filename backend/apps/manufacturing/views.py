from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.manufacturing.models import MaterialIssue, ProductionOrder, ProductionOutput, ProductionStep
from apps.manufacturing.serializers import (
    MaterialIssueSerializer,
    ProductionOrderSerializer,
    ProductionOutputSerializer,
    ProductionStepSerializer,
)


class ProductionOrderViewSet(TenantViewSet):
    queryset = ProductionOrder.objects.select_related("product")
    serializer_class = ProductionOrderSerializer
    required_permission = "manufacturing.view"
    write_permission = "manufacturing.manage"
    search_fields = ["number", "product__sku", "product__name"]
    filterset_fields = ["status", "priority", "product"]
    ordering_fields = ["created_at", "due_date", "quantity"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = dict(qs.values_list("status").annotate(n=Count("id")))
        total_qty = qs.aggregate(v=Sum("quantity"))["v"] or 0
        output_qty = (
            ProductionOutput.objects.filter(organization=request.organization).aggregate(v=Sum("quantity"))["v"] or 0
        )
        overdue = qs.filter(
            status__in=["released", "in_progress"], due_date__lt=timezone.now().date()
        ).count()
        return Response(
            {
                "total": qs.count(),
                "draft": by_status.get("draft", 0),
                "released": by_status.get("released", 0),
                "in_progress": by_status.get("in_progress", 0),
                "completed": by_status.get("completed", 0),
                "cancelled": by_status.get("cancelled", 0),
                "total_quantity": float(total_qty),
                "output_quantity": float(output_qty),
                "overdue": overdue,
                "priority_breakdown": list(
                    qs.values("priority").annotate(count=Count("id")).order_by("priority")
                ),
            }
        )

    @action(detail=True, methods=["post"])
    def release(self, request, pk=None):
        order = self.get_object()
        if order.status != ProductionOrder.Status.DRAFT:
            return Response({"detail": "Only draft orders can be released."}, status=400)
        order.status = ProductionOrder.Status.RELEASED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        order = self.get_object()
        if order.status != ProductionOrder.Status.RELEASED:
            return Response({"detail": "Only released orders can be started."}, status=400)
        order.status = ProductionOrder.Status.IN_PROGRESS
        order.start_date = request.data.get("start_date") or timezone.now().date()
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        order = self.get_object()
        if order.status not in (ProductionOrder.Status.RELEASED, ProductionOrder.Status.IN_PROGRESS):
            return Response({"detail": "Order is not in a completable state."}, status=400)
        order.status = ProductionOrder.Status.COMPLETED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)


class ProductionStepViewSet(TenantViewSet):
    queryset = ProductionStep.objects.select_related("order", "order__product")
    serializer_class = ProductionStepSerializer
    required_permission = "manufacturing.view"
    write_permission = "manufacturing.manage"
    search_fields = ["operation", "order__number"]
    filterset_fields = ["order", "status"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        step = self.get_object()
        step.status = ProductionStep.Status.COMPLETED
        step.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(step).data)


class ProductionOutputViewSet(TenantViewSet):
    queryset = ProductionOutput.objects.select_related("order", "product")
    serializer_class = ProductionOutputSerializer
    required_permission = "manufacturing.view"
    write_permission = "manufacturing.manage"
    search_fields = ["batch_number", "order__number", "product__sku"]
    filterset_fields = ["order", "product"]


class MaterialIssueViewSet(TenantViewSet):
    queryset = MaterialIssue.objects.select_related("order", "product", "issued_by")
    serializer_class = MaterialIssueSerializer
    required_permission = "manufacturing.view"
    write_permission = "manufacturing.manage"
    search_fields = ["order__number", "product__sku", "from_bin"]
    filterset_fields = ["order", "product"]
