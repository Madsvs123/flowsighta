from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.dock_scheduling.models import Dock, DockAppointment


class DockSerializer(TenantSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    appointment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Dock
        fields = (
            "id",
            "warehouse",
            "warehouse_name",
            "code",
            "type",
            "is_active",
            "appointment_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class DockAppointmentSerializer(TenantSerializer):
    dock_code = serializers.CharField(source="dock.code", read_only=True)
    warehouse_name = serializers.CharField(source="dock.warehouse.name", read_only=True)

    class Meta:
        model = DockAppointment
        fields = (
            "id",
            "dock",
            "dock_code",
            "warehouse_name",
            "carrier",
            "vehicle",
            "window_start",
            "window_end",
            "status",
            "reference",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
