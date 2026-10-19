from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.fleet.models import Driver, FuelLog, Vehicle, VehicleMaintenance
from apps.fleet.serializers import (
    DriverSerializer,
    FuelLogSerializer,
    VehicleMaintenanceSerializer,
    VehicleSerializer,
)


class VehicleViewSet(TenantViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    required_permission = "fleet.view"
    write_permission = "fleet.manage"
    search_fields = ["plate", "type"]
    filterset_fields = ["type", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        org = request.organization
        return Response(
            {
                "vehicle_count": qs.count(),
                "by_status": {status: qs.filter(status=status).count() for status, _ in Vehicle.Status.choices},
                "active_drivers": Driver.objects.filter(organization=org, status=Driver.Status.ACTIVE).count(),
                "open_maintenance": VehicleMaintenance.objects.filter(
                    organization=org, status__in=["scheduled", "in_progress"]
                ).count(),
                "fuel_cost_ytd": float(
                    FuelLog.objects.filter(organization=org, date__year=timezone.now().year).aggregate(
                        v=Sum("gallons")
                    )["v"]
                    or 0
                ),
            }
        )

    @action(detail=True, methods=["post"])
    def maintain(self, request, pk=None):
        vehicle = self.get_object()
        if vehicle.status != Vehicle.Status.RETIRED:
            return Response({"detail": "Retired vehicles cannot enter maintenance."}, status=400)
        vehicle.status = Vehicle.Status.MAINTENANCE
        vehicle.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(vehicle).data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        vehicle = self.get_object()
        if vehicle.status == Vehicle.Status.RETIRED:
            return Response({"detail": "Retired vehicles cannot be reactivated."}, status=400)
        vehicle.status = Vehicle.Status.ACTIVE
        vehicle.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(vehicle).data)


class DriverViewSet(TenantViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    required_permission = "fleet.view"
    write_permission = "fleet.manage"
    search_fields = ["name", "license_number", "phone"]
    filterset_fields = ["status", "license_class"]

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        driver = self.get_object()
        driver.status = Driver.Status.SUSPENDED
        driver.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(driver).data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        driver = self.get_object()
        driver.status = Driver.Status.ACTIVE
        driver.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(driver).data)


class VehicleMaintenanceViewSet(TenantViewSet):
    queryset = VehicleMaintenance.objects.select_related("vehicle")
    serializer_class = VehicleMaintenanceSerializer
    required_permission = "fleet.view"
    write_permission = "fleet.manage"
    search_fields = ["vehicle__plate", "type"]
    filterset_fields = ["vehicle", "type", "status"]

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        record = self.get_object()
        if record.status == VehicleMaintenance.Status.COMPLETED:
            return Response({"detail": "Completed records cannot be restarted."}, status=400)
        record.status = VehicleMaintenance.Status.IN_PROGRESS
        record.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(record).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        record = self.get_object()
        record.status = VehicleMaintenance.Status.COMPLETED
        record.completed_date = timezone.now().date()
        record.save(update_fields=["status", "completed_date", "updated_at"])
        return Response(self.get_serializer(record).data)


class FuelLogViewSet(TenantViewSet):
    queryset = FuelLog.objects.select_related("vehicle")
    serializer_class = FuelLogSerializer
    required_permission = "fleet.view"
    write_permission = "fleet.manage"
    search_fields = ["vehicle__plate"]
    filterset_fields = ["vehicle", "date"]
