from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.dock_scheduling.models import Dock, DockAppointment
from apps.dock_scheduling.serializers import DockAppointmentSerializer, DockSerializer


class DockViewSet(TenantViewSet):
    queryset = Dock.objects.select_related("warehouse").annotate(appointment_count=Count("appointments"))
    serializer_class = DockSerializer
    required_permission = "dock_scheduling.view"
    write_permission = "dock_scheduling.manage"
    search_fields = ["code", "warehouse__name", "warehouse__code"]
    filterset_fields = ["warehouse", "type", "is_active"]


class DockAppointmentViewSet(TenantViewSet):
    queryset = DockAppointment.objects.select_related("dock", "dock__warehouse")
    serializer_class = DockAppointmentSerializer
    required_permission = "dock_scheduling.view"
    write_permission = "dock_scheduling.manage"
    search_fields = ["reference", "carrier", "vehicle", "driver", "dock__code"]
    filterset_fields = ["dock", "status", "carrier"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        now = timezone.now()
        return Response(
            {
                "appointments": qs.count(),
                "today": qs.filter(
                    Q(window_start__date=now.date()) & Q(window_end__date=now.date())
                ).count(),
                "scheduled": qs.filter(status=DockAppointment.Status.SCHEDULED).count(),
                "active": qs.filter(
                    status__in=[DockAppointment.Status.ARRIVED, DockAppointment.Status.LOADING]
                ).count(),
                "completed": qs.filter(status=DockAppointment.Status.COMPLETED).count(),
                "no_shows": qs.filter(status=DockAppointment.Status.NO_SHOW).count(),
                "docks": Dock.objects.filter(organization=request.organization, is_active=True).count(),
                "upcoming": qs.filter(
                    window_start__gte=now,
                    status__in=[
                        DockAppointment.Status.SCHEDULED,
                        DockAppointment.Status.ARRIVED,
                        DockAppointment.Status.LOADING,
                    ],
                ).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def arrive(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = DockAppointment.Status.ARRIVED
        appointment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(appointment).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = DockAppointment.Status.COMPLETED
        appointment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(appointment).data)

    @action(detail=True, methods=["post"])
    def no_show(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = DockAppointment.Status.NO_SHOW
        appointment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(appointment).data)
