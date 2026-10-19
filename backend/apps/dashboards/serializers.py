from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.dashboards.models import Dashboard, DashboardShare, DashboardWidget, WidgetDataSource


class DashboardSerializer(TenantSerializer):
    widget_count = serializers.IntegerField(read_only=True)
    share_count = serializers.IntegerField(read_only=True)
    owner_name = serializers.CharField(source="owner.first_name", read_only=True)

    class Meta:
        model = Dashboard
        fields = (
            "id",
            "name",
            "is_default",
            "owner",
            "owner_name",
            "widget_count",
            "share_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class DashboardWidgetSerializer(TenantSerializer):
    dashboard_name = serializers.CharField(source="dashboard.name", read_only=True)

    class Meta:
        model = DashboardWidget
        fields = (
            "id",
            "dashboard",
            "dashboard_name",
            "type",
            "config",
            "position",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class WidgetDataSourceSerializer(TenantSerializer):
    widget_type = serializers.CharField(source="widget.type", read_only=True)

    class Meta:
        model = WidgetDataSource
        fields = ("id", "widget", "widget_type", "source_ref", "params", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class DashboardShareSerializer(TenantSerializer):
    dashboard_name = serializers.CharField(source="dashboard.name", read_only=True)
    user_name = serializers.CharField(source="user.first_name", read_only=True)

    class Meta:
        model = DashboardShare
        fields = ("id", "dashboard", "dashboard_name", "user", "user_name", "role", "created_at")
        read_only_fields = ("id", "created_at")
