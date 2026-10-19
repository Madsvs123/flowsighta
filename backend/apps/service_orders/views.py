from django.db.models import Avg, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.service_orders.models import (
    FieldReport,
    ServiceAppointment,
    ServiceLine,
    ServiceOrder,
)
from apps.service_orders.serializers import (
    FieldReportSerializer,
    ServiceAppointmentSerializer,
    ServiceLineSerializer,
    ServiceOrderSerializer,
)


class ServiceOrderViewSet(TenantViewSet):
    queryset = ServiceOrder.objects.select_related("technician").prefetch_related("lines")
    serializer_class = ServiceOrderSerializer
    required_permission = "service_orders.view"
    write_permission = "service_orders.manage"
    search_fields = ["number", "customer_ref"]
    filterset_fields = ["status", "type", "technician", "scheduled_at"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        today = timezone.localdate()
        agg = qs.aggregate(labor_hours=Sum("lines__labor_hours"), line_total=Avg("lines__line_total"))
        return Response(
            {
                "orders": qs.count(),
                "scheduled": qs.filter(status=ServiceOrder.Status.SCHEDULED).count(),
                "dispatched": qs.filter(status=ServiceOrder.Status.DISPATCHED).count(),
                "in_progress": qs.filter(status=ServiceOrder.Status.IN_PROGRESS).count(),
                "completed": qs.filter(status=ServiceOrder.Status.COMPLETED).count(),
                "cancelled": qs.filter(status=ServiceOrder.Status.CANCELLED).count(),
                "due_today": qs.filter(
                    status__in=[
                        ServiceOrder.Status.SCHEDULED,
                        ServiceOrder.Status.DISPATCHED,
                        ServiceOrder.Status.IN_PROGRESS,
                    ],
                    scheduled_at__date=today,
                ).count(),
                "labor_hours": float(agg["labor_hours"] or 0),
                "line_total": float(agg["line_total"] or 0),
            }
        )

    @action(detail=True, methods=["post"])
    def dispatch(self, request, pk=None):
        order = self.get_object()
        if order.status != ServiceOrder.Status.SCHEDULED:
            raise ValidationError("Only scheduled orders can be dispatched.")
        technician_id = request.data.get("technician_id")
        if technician_id:
            order.technician_id = technician_id
        order.status = ServiceOrder.Status.DISPATCHED
        order.updated_by = request.user
        order.save(update_fields=["status", "technician", "updated_at", "updated_by"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        order = self.get_object()
        if order.status != ServiceOrder.Status.DISPATCHED:
            raise ValidationError("Only dispatched orders can be started.")
        order.status = ServiceOrder.Status.IN_PROGRESS
        order.updated_by = request.user
        order.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        order = self.get_object()
        if order.status != ServiceOrder.Status.IN_PROGRESS:
            raise ValidationError("Only in-progress orders can be completed.")
        order.status = ServiceOrder.Status.COMPLETED
        order.updated_by = request.user
        order.save(update_fields=["status", "updated_at", "updated_by"])
        FieldReport.objects.update_or_create(
            organization=order.organization,
            order=order,
            defaults={"completed_at": timezone.now(), "notes": request.data.get("notes", "")},
        )
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in (ServiceOrder.Status.COMPLETED, ServiceOrder.Status.CANCELLED):
            raise ValidationError("Completed or cancelled orders cannot be cancelled.")
        order.status = ServiceOrder.Status.CANCELLED
        order.updated_by = request.user
        order.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(order).data)


class ServiceLineViewSet(TenantViewSet):
    queryset = ServiceLine.objects.select_related("order")
    serializer_class = ServiceLineSerializer
    required_permission = "service_orders.view"
    write_permission = "service_orders.manage"
    search_fields = ["description", "order__number"]
    filterset_fields = ["order"]


class ServiceAppointmentViewSet(TenantViewSet):
    queryset = ServiceAppointment.objects.select_related("order")
    serializer_class = ServiceAppointmentSerializer
    required_permission = "service_orders.view"
    write_permission = "service_orders.manage"
    search_fields = ["order__number", "location"]
    filterset_fields = ["order", "status"]

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status != ServiceAppointment.Status.SCHEDULED:
            raise ValidationError("Only scheduled appointments can be confirmed.")
        appointment.status = ServiceAppointment.Status.CONFIRMED
        appointment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(appointment).data)

    @action(detail=True, methods=["post"])
    def done(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status not in (
            ServiceAppointment.Status.SCHEDULED,
            ServiceAppointment.Status.CONFIRMED,
        ):
            raise ValidationError("Only scheduled or confirmed appointments can be marked done.")
        appointment.status = ServiceAppointment.Status.DONE
        appointment.end_at = request.data.get("end_at") or timezone.now()
        appointment.save(update_fields=["status", "end_at", "updated_at"])
        return Response(self.get_serializer(appointment).data)


class FieldReportViewSet(TenantViewSet):
    queryset = FieldReport.objects.select_related("order")
    serializer_class = FieldReportSerializer
    required_permission = "service_orders.view"
    write_permission = "service_orders.manage"
    search_fields = ["notes", "order__number"]
    filterset_fields = ["order"]
