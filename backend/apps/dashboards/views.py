from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.dashboards.models import Dashboard, DashboardShare, DashboardWidget, WidgetDataSource
from apps.dashboards.serializers import (
    DashboardSerializer,
    DashboardShareSerializer,
    DashboardWidgetSerializer,
    WidgetDataSourceSerializer,
)


class DashboardViewSet(TenantViewSet):
    queryset = Dashboard.objects.select_related("owner").annotate(
        widget_count=Count("widgets", distinct=True), share_count=Count("shares", distinct=True)
    )
    serializer_class = DashboardSerializer
    required_permission = "dashboards.view"
    write_permission = "dashboards.manage"
    search_fields = ["name"]
    filterset_fields = ["is_default", "owner"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        dashboards = self.get_queryset()
        widgets = DashboardWidget.objects.filter(organization=request.organization)
        shares = DashboardShare.objects.filter(organization=request.organization)
        return Response(
            {
                "dashboard_count": dashboards.count(),
                "default_dashboards": dashboards.filter(is_default=True).count(),
                "widget_count": widgets.count(),
                "widgets_by_type": {
                    t: widgets.filter(type=t).count() for t, _ in DashboardWidget.Type.choices
                },
                "share_count": shares.count(),
                "data_source_count": WidgetDataSource.objects.filter(organization=request.organization).count(),
                "top_dashboards": list(
                    dashboards.order_by("widget_count")[:5].values("name", "widget_count", "is_default")
                ),
            }
        )

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        dashboard = self.get_object()
        Dashboard.objects.filter(organization=request.organization, is_default=True).update(
            is_default=False
        )
        dashboard.is_default = True
        dashboard.save(update_fields=["is_default", "updated_at"])
        return Response(self.get_serializer(dashboard).data)


class DashboardWidgetViewSet(TenantViewSet):
    queryset = DashboardWidget.objects.select_related("dashboard")
    serializer_class = DashboardWidgetSerializer
    required_permission = "dashboards.view"
    write_permission = "dashboards.manage"
    search_fields = ["dashboard__name"]
    filterset_fields = ["dashboard", "type"]


class WidgetDataSourceViewSet(TenantViewSet):
    queryset = WidgetDataSource.objects.select_related("widget")
    serializer_class = WidgetDataSourceSerializer
    required_permission = "dashboards.view"
    write_permission = "dashboards.manage"
    search_fields = ["source_ref", "widget__dashboard__name"]
    filterset_fields = ["widget"]


class DashboardShareViewSet(TenantViewSet):
    queryset = DashboardShare.objects.select_related("dashboard", "user")
    serializer_class = DashboardShareSerializer
    required_permission = "dashboards.view"
    write_permission = "dashboards.manage"
    search_fields = ["dashboard__name", "user__email"]
    filterset_fields = ["dashboard", "user", "role"]
