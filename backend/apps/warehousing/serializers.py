from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.warehousing.models import Bin, PutawayRule, StorageZone


class StorageZoneSerializer(TenantSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)

    class Meta:
        model = StorageZone
        fields = (
            "id",
            "warehouse",
            "warehouse_name",
            "warehouse_code",
            "code",
            "name",
            "type",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class BinSerializer(TenantSerializer):
    zone_code = serializers.CharField(source="zone.code", read_only=True)
    warehouse_name = serializers.CharField(source="zone.warehouse.name", read_only=True)

    class Meta:
        model = Bin
        fields = (
            "id",
            "zone",
            "zone_code",
            "warehouse_name",
            "code",
            "capacity",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PutawayRuleSerializer(TenantSerializer):
    zone_code = serializers.CharField(source="zone.name", read_only=True)

    class Meta:
        model = PutawayRule
        fields = ("id", "name", "category", "zone", "zone_code", "priority", "created_at")
        read_only_fields = ("id", "created_at")
