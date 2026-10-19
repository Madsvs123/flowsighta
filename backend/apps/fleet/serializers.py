from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.fleet.models import Driver, FuelLog, Vehicle, VehicleMaintenance


class VehicleSerializer(TenantSerializer):
    maintenance_count = serializers.IntegerField(source="fuel_logs.count", read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            "id",
            "plate",
            "type",
            "capacity",
            "status",
            "odometer",
            "maintenance_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class DriverSerializer(TenantSerializer):
    class Meta:
        model = Driver
        fields = (
            "id",
            "name",
            "license_number",
            "license_class",
            "phone",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class VehicleMaintenanceSerializer(TenantSerializer):
    vehicle_plate = serializers.CharField(source="vehicle.plate", read_only=True)
    vehicle_type = serializers.CharField(source="vehicle.type", read_only=True)

    class Meta:
        model = VehicleMaintenance
        fields = (
            "id",
            "vehicle",
            "vehicle_plate",
            "vehicle_type",
            "type",
            "odometer",
            "scheduled_date",
            "completed_date",
            "cost",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class FuelLogSerializer(TenantSerializer):
    vehicle_plate = serializers.CharField(source="vehicle.plate", read_only=True)

    class Meta
        model = FuelLog
        fields = ("id", "vehicle", "vehicle_plate", "date", "gallons", "cost", "odometer", "created_at")
        read_only_fields = ("id", "created_at", "cost")
