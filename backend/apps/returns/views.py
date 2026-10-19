from django.db.models import Count, Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.returns.models import RestockTask, ReturnLine, ReturnOrder
from apps.returns.serializers import RestockTaskSerializer, ReturnLineSerializer, ReturnOrderSerializer


class ReturnOrderViewSet(TenantViewSet):
    queryset = ReturnOrder.objects.select_related("created_by").annotate(
        line_count=Count("lines"),
        total_quantity=Sum("lines__quantity"),
    )
    serializer_class = ReturnOrderSerializer
    required_permission = "returns.view"
    write_permission = "returns.manage"
    search_fields = ["number", "reference", "reason", "created_by__email"]
    filterset_fields = ["status", "type", "created_by"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        lines = ReturnLine.objects.filter(organization=request.organization)
        tasks = RestockTask.objects.filter(organization=request.organization)
        return Response(
            {
                "returns": qs.count(),
                "requested": qs.filter(status=ReturnOrder.Status.REQUESTED).count(),
                "in_flow": qs.filter(
                    status__in=[
                        ReturnOrder.Status.APPROVED,
                        ReturnOrder.Status.RECEIVED,
                        ReturnOrder.Status.INSPECTED,
                    ]
                ).count(),
                "restocked": qs.filter(status=ReturnOrder.Status.RESTOCKED).count(),
                "closed": qs.filter(status=ReturnOrder.Status.CLOSED).count(),
                "rejected": qs.filter(status=ReturnOrder.Status.REJECTED).count(),
                "units_returned": float(lines.aggregate(total=Count("quantity"))["total"] or 0),
                "pending_restock": tasks.filter(status=RestockTask.Status.PENDING).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        order = self.get_object()
        order.status = ReturnOrder.Status.APPROVED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        order = self.get_object()
        order.status = ReturnOrder.Status.CLOSED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        order = self.get_object()
        order.status = ReturnOrder.Status.REJECTED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)


class ReturnLineViewSet(TenantViewSet):
    queryset = ReturnLine.objects.select_related("order", "product")
    serializer_class = ReturnLineSerializer
    required_permission = "returns.view"
    write_permission = "returns.manage"
    search_fields = ["order__number", "product__sku"]
    filterset_fields = ["order", "product", "condition", "disposition"]


class RestockTaskViewSet(TenantViewSet):
    queryset = RestockTask.objects.select_related("line", "line__order", "line__product", "warehouse")
    serializer_class = RestockTaskSerializer
    required_permission = "returns.view"
    write_permission = "returns.manage"
    search_fields = ["line__order__number", "line__product__sku", "bin"]
    filterset_fields = ["status", "warehouse", "line"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = RestockTask.Status.COMPLETED
        task.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(task).data
