from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.resources.models import Resource, ResourceAllocation, ResourceCalendar, ResourceSkill


class ResourceSerializer(TenantSerializer):
    class Meta:
        model = Resource
        fields = ("id", "name", "type", "cost_rate", "status", "created_at")
        read_only_fields = ("id", "created_at")


class ResourceSkillSerializer(TenantSerializer):
    resource_name = serializers.CharField(source="resource.name", read_only=True)

    class Meta:
        model = ResourceSkill
        fields = ("id", "resource", "resource_name", "skill", "level", "created_at")
        read_only_fields = ("id", "created_at")


class ResourceAllocationSerializer(TenantSerializer):
    resource_name = serializers.CharField(source="resource.name", read_only=True)
    resource_type = serializers.CharField(source="resource.resource_type", read_only=True)

    class Meta:
        model = ResourceAllocation
        fields = (
            "id",
            "resource",
            "resource_name",
            "resource_type",
            "project_ref",
            "start_date",
            "end_date",
            "hours_per_week",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ResourceCalendarSerializer(TenantSerializer):
    resource_name = serializers.CharField(source="resource.name", read_only=True)

    class Meta:
        model = ResourceCalendar
        fields = ("id", "resource", "resource_name", "date", "available_hours", "created_at")
        read_only_fields = ("id", "created_at")
