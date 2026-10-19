from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.work_orders.models import WorkOrder, WorkOrderLabor, WorkOrderTask
from apps.work_orders.serializers import (
    WorkOrderLaborSerializer,
    WorkOrderSerializer,
    WorkOrderTaskSerializer,
)


class WorkOrderViewSet(TenantViewSet):
    queryset = WorkOrder.objects.select_related("assigned_to").prefetch_related("tasks", "labor")
    serializer_class = WorkOrderSerializer
    required_permission = "work_orders.view"
    write_permission = "work_orders.manage"
    search_fields = ["number", "type"]
    filterset_fields = ["status", "priority", "type", "assigned_to"]
    ordering_fields = ["created_at", "due_date", "priority"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = dict(qs.values_list("status").annotate(n=Count("id")))
        overdue = qs.filter(
            status__in=["open", "assigned", "in_progress", "on_hold"],
            due_date__lt=timezone.now().date(),
        ).count()
        labor = (
            WorkOrderLabor.objects.filter(organization=request.organization).aggregate(v=Sum("hours"))["v"] or 0
        )
        return Response(
            {
                "total": qs.count(),
                "open": by_status.get("open", 0),
                "assigned": by_status.get("assigned", 0),
                "in_progress": by_status.get("in_progress", 0),
                "on_hold": by_status.get("on_hold", 0),
                "completed": by_status.get("completed", 0),
                "cancelled": by_status.get("cancelled", 0),
                "overdue": overdue,
                "labor_hours": float(labor),
                "type_breakdown": list(qs.values("type").annotate(count=Count("id")).order_by("type")),
            }
        )

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        order = self.get_object()
        user_id = request.data.get("user")
        if not user_id:
            return Response({"detail": "assigned_to is required."}, status=400)
        order.assigned_to_id = user_id
        if order.status == WorkOrder.Status.OPEN:
            order.status = WorkOrder.Status.ASSIGNED
        order.save(update_fields=["assigned_to", "status", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        order = self.get_object()
        if order.status not in (WorkOrder.Status.OPEN, WorkOrder.Status.ASSIGNED, WorkOrder.Status.ON_HOLD):
            return Response({"detail": "Order cannot be started from current state."}, status=400)
        order.status = WorkOrder.Status.IN_PROGRESS
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        order = self.get_object()
        if order.status == WorkOrder.Status.COMPLETED:
            return Response({"detail": "Order is already completed."}, status=400)
        order.status = WorkOrder.Status.COMPLETED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)


class WorkOrderTaskViewSet(TenantViewSet):
    queryset = WorkOrderTask.objects.select_related("order")
    serializer_class = WorkOrderTaskSerializer
    required_permission = "work_orders.view"
    write_permission = "work_orders.manage"
    search_fields = ["description", "order__number"]
    filterset_fields = ["order", "status"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = WorkOrderTask.Status.COMPLETED
        task.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(task).data)


class WorkOrderLaborViewSet(TenantViewSet):
    queryset = WorkOrderLabor.objects.select_related("order", "user")
    serializer_class = WorkOrderLaborSerializer
    required_permission = "work_orders.view"
    write_permission = "work_orders.manage"
    search_fields = ["order__number", "user__email"]
    filterset_fields = ["order", "user", "hours"]
