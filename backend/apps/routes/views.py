from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.routes.models import DeliveryStop, DriverAssignment, Route, RouteStop
from apps.routes.serializers import (
    DeliveryStopSerializer,
    DriverAssignmentSerializer,
    RouteSerializer,
    RouteStopSerializer,
)


class RouteViewSet(TenantViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    required_permission = "routes.view"
    write_permission = "routes.manage"
    search_fields = ["code", "name", "origin", "destination"]
    filterset_fields = ["is_active"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        org = request.organization
        assignments = DriverAssignment.objects.filter(organization=org)
        deliveries = DeliveryStop.objects.filter(organization=org)
        return Response(
            {
                "route_count": qs.count(),
                "active_routes": qs.filter(is_active=True).count(),
                "stop_count": RouteStop.objects.filter(organization=org).count(),
                "assignments_today": assignments.filter(
                    scheduled_date=timezone.now().date(), status__in=["assigned", "in_progress"]
                ).count(),
                "delivered_stops": deliveries.filter(status=DeliveryStop.Status.DELIVERED).count(),
                "pending_stops": deliveries.filter(status=DeliveryStop.Status.PENDING).count(),
            }
        )


class RouteStopViewSet(TenantViewSet):
    queryset = RouteStop.objects.select_related("route")
    serializer_class = RouteStopSerializer
    required_permission = "routes.view"
    write_permission = "routes.manage"
    search_fields = ["location_name", "route__code", "route__name"]
    filterset_fields = ["route"]


class DriverAssignmentViewSet(TenantViewSet):
    queryset = DriverAssignment.objects.select_related("route", "driver")
    serializer_class = DriverAssignmentSerializer
    required_permission = "routes.view"
    write_permission = "routes.manage"
    search_fields = ["route__code", "route__name", "driver__email", "vehicle"]
    filterset_fields = ["route", "driver", "status", "scheduled_date"]

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        assignment = self.get_object()
        if assignment.status != DriverAssignment.Status.ASSIGNED:
            return Response({"detail": "Only assigned assignments can be started."}, status=400)
        assignment.status = DriverAssignment.Status.IN_PROGRESS
        assignment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(assignment).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        assignment = self.get_object()
        if assignment.status == DriverAssignment.Status.COMPLETED:
            return Response({"detail": "Cancelled assignments cannot be completed."}, status=400)
        assignment.status = DriverAssignment.Status.COMPLETED
        assignment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(assignment).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        assignment = self.get_object()
        if assignment.status in (DriverAssignment.Status.COMPLETED, DriverAssignment.Status.CANCELLED):
            return Response({"detail": "Assignment is already finalized."}, status=400)
        assignment.status = DriverAssignment.Status.CANCELLED
        assignment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(assignment).data)


class DeliveryStopViewSet(TenantViewSet):
    queryset = DeliveryStop.objects.select_related("route")
    serializer_class = DeliveryStopSerializer
    required_permission = "routes.view"
    write_permission = "routes.manage"
    search_fields = ["address", "contact", "route__code", "pod_reference"]
    filterset_fields = ["route", "status"]

    @action(detail=True, methods=["post"])
    def arrive(self, request, pk=None):
        stop = self.get_object()
        if stop.status == DeliveryStop.Status.DELIVERED:
            return Response({"detail": "Already delivered."}, status=400)
        stop.status = DeliveryStop.Status.ARRIVED
        stop.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(stop).data)

    @action(detail=True, methods=["post"])
    def deliver(self, request, pk=None):
        stop = self.get_object()
        stop.status = DeliveryStop.Status.DELIVERED
        stop.pod_reference = request.data.get("pod_reference", stop.pod_reference or "")
        stop.delivered_at = timezone.now()
        stop.save(update_fields=["status", "pod_reference", "delivered_at", "updated_at"])
        return Response(self.get_serializer(stop).data)

    @action(detail=True, methods=["post"])
    def fail(self, request, pk=None):
        stop = self.get_object()
        if stop.status == DeliveryStop.Status.DELIVERED:
            return Response({"detail": "Delivered stops cannot be failed."}, status=400)
        stop.status = DeliveryStop.Status.FAILED
        stop.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(stop).data
