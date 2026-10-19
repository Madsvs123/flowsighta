from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.maintenance.models import Equipment, MaintenanceLog, MaintenanceOrder, MaintenancePlan
from apps.maintenance.serializers import (
    EquipmentSerializer,
    MaintenanceLogSerializer,
    MaintenanceOrderSerializer,
    MaintenancePlanSerializer,
)


class EquipmentViewSet(TenantViewSet):
    queryset = Equipment.objects.prefetch_related("maintenance_plans", "maintenance_orders")
    serializer_class = EquipmentSerializer
    required_permission = "maintenance.view"
    write_permission = "maintenance.manage"
    search_fields = ["code", "name", "type", "location"]
    filterset_fields = ["status", "type"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = dict(qs.values_list("status").annotate(n=Count("id")))
        orders = MaintenanceOrder.objects.filter(organization=request.organization)
        order_by_status = dict(orders.values_list("status").annotate(n=Count("id")))
        cost = orders.aggregate(v=Sum("cost"))["v"] or 0
        return Response(
            {
                "equipment_total": qs.count(),
                "operational": by_status.get("operational", 0),
                "in_maintenance": by_status.get("maintenance", 0),
                "out_of_service": by_status.get("out_of_service", 0),
                "plans_active": MaintenancePlan.objects.filter(
                    organization=request.organization, is_active=True
                ).count(),
                "orders_total": orders.count(),
                "orders_scheduled": order_by_status.get("scheduled", 0),
                "orders_in_progress": order_by_status.get("in_progress", 0),
                "orders_completed": order_by_status.get("completed", 0),
                "orders_overdue": order_by_status.get("overdue", 0),
                "total_cost": float(cost),
                "status_breakdown": [
                    {"status": k, "count": v} for k, v in order_by_status.items()
                ],
            }
        )

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        equipment = self.get_object()
        status = request.data.get("status")
        if status not in Equipment.Status.values:
            return Response({"detail": "Invalid status."}, status=400)
        equipment.status = status
        equipment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(equipment).data)


class MaintenancePlanViewSet(TenantViewSet):
    queryset = MaintenancePlan.objects.select_related("equipment")
    serializer_class = MaintenancePlanSerializer
    required_permission = "maintenance.view"
    write_permission = "maintenance.manage"
    search_fields = ["equipment__code", "equipment__name", "description"]
    filterset_fields = ["equipment", "type", "is_active"]

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        plan = self.get_object()
        plan.is_active = True
        plan.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(plan).data)


class MaintenanceOrderViewSet(TenantViewSet):
    queryset = MaintenanceOrder.objects.select_related("equipment", "plan")
    serializer_class = MaintenanceOrderSerializer
    required_permission = "maintenance.view"
    write_permission = "maintenance.manage"
    search_fields = ["equipment__code", "equipment__name"]
    filterset_fields = ["equipment", "plan", "status"]

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        order = self.get_object()
        order.status = MaintenanceOrder.Status.IN_PROGRESS
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        order = self.get_object()
        order.status = MaintenanceOrder.Status.COMPLETED
        order.completed_date = timezone.now().date()
        order.cost = request.data.get("cost", 0)
        order.save(update_fields=["status", "completed_date", "cost", "updated_at"])
        if order.equipment.status == Equipment.Status.MAINTENANCE:
            order.equipment.status = Equipment.Status.OPERATIONAL
            order.equipment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)


class MaintenanceLogViewSet(TenantViewSet):
    queryset = MaintenanceLog.objects.select_related("order", "order__equipment", "performed_by")
    serializer_class = MaintenanceLogSerializer
    required_permission = "maintenance.view"
    write_permission = "maintenance.manage"
    search_fields = ["notes", "order__equipment__code"]
    filterset_fields = ["order", "performed_by"]
