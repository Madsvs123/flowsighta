from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.yard.models import YardGateLog, YardLocation, YardMove


class YardLocationSerializer(TenantSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    move_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = YardLocation
        fields = (
            "id",
            "warehouse",
            "warehouse_name",
            "code",
            "type",
            "is_active",
            "move_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class YardMoveSerializer(TenantSerializer):
    location_code = serializers.CharField(source="location.code", read_only=True)
    location_type = serializers.CharField(source="location.type", read_only=True)
    warehouse_name = serializers.CharField(source="location.warehouse.name", read_only=True)

    class Meta:
        model = YardMove
        fields = (
            "id",
            "location",
            "location_code",
            "location_type",
            "warehouse_name",
            "vehicle",
            "trailer",
            "direction",
            "status",
            "moved_at",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")


class YardGateLogSerializer(TenantSerializer):
    class Meta:
        model = YardGateLog
        fields = (
            "id",
            "vehicle",
            "trailer",
            "direction",
            "driver",
            "occurred_at",
            "gate",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
