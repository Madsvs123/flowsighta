from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.routes.models import DeliveryStop, DriverAssignment, Route, RouteStop


class RouteSerializer(TenantSerializer):
    stop_count = serializers.IntegerField(source="stops.count", read_only=True)

    class Meta:
        model = Route
        fields = (
            "id",
            "code",
            "name",
            "origin",
            "destination",
            "distance_km",
            "is_active",
            "stop_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class RouteStopSerializer(TenantSerializer):
    route_code = serializers.CharField(source="route.code", read_only=True)
    route_name = serializers.CharField(source="route.name", read_only=True)

    class Meta:
        model = RouteStop
        fields = (
            "id",
            "route",
            "route_code",
            "route_name",
            "sequence",
            "location_name",
            "eta_minutes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class DriverAssignmentSerializer(TenantSerializer):
    route_code = serializers.CharField(source="route.code", read_only=True)
    route_name = serializers.CharField(source="route.name", read_only=True
    driver_name = serializers.CharField(source="driver.fullname", read_only=True)
    driver_email = serializers.CharField(source="driver.email", read_only=True)

    class Meta:
        model = DriverAssignment
        fields = (
            "id",
            "route",
            "route_code",
            "route_name",
            "driver",
            "driver_name",
            "driver_email",
            "vehicle",
            "scheduled_date",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class DeliveryStopSerializer(TenantSerializer):
    route_code = serializers.CharField(source="route.code", read_only=True)
    route_name = serializers.CharField(source="route.name", read_only=True)

    class Meta:
        model = DeliveryStop
        fields = (
            "id",
            "route",
            "route_code",
            "route_name",
            "address",
            "contact",
            "status",
            "pod_reference",
            "delivered_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
