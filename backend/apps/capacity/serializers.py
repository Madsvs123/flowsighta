from rest_framework import serializers

from apps.capacity.models import CapacityLoad, CapacityPlan, CapacityProfile
from apps.core.mixins import TenantSerializer


class CapacityProfileSerializer(TenantSerializer):
    class Meta:
        model = CapacityProfile
        fields = (
            "id",
            "name",
            "workcenter",
            "available_hours",
            "efficiency_pct",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CapacityLoadSerializer(TenantSerializer):
    profile_name = serializers.CharField(source="profile.name", read_only=True)
    workcenter = serializers.CharField(source="profile.workcenter", read_only=True)

    class Meta:
        model = CapacityLoad
        fields = (
            "id",
            "profile",
            "profile_name",
            "workcenter",
            "date",
            "load_hours",
            "available_hours",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "load_hours")


class CapacityPlanSerializer(TenantSerializer):
    profile_name = serializers.CharField(source="profile.name", read_only=True)
    workcenter = serializers.CharField(source="profile.workcenter", read_only=True)

    class Meta:
        model = CapacityPlan
        fields = (
            "id",
            "profile",
            "profile_name",
            "workcenter",
            "period_start",
            "period_end",
            "planned_hours",
            "actual_hours",
            "utilization_pct",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
