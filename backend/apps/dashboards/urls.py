from rest_framework.routers import DefaultRouter

from apps.dashboards.views import (
    DashboardShareViewSet,
    DashboardViewSet,
    DashboardWidgetViewSet,
    WidgetDataSourceViewSet,
)

router = DefaultRouter()
router.register("dashboards", DashboardViewSet, basename="dashboard")
router.register("dashboard-widgets", DashboardWidgetViewSet, basename="widgets")
router.register("widget-data-sources", WidgetDataSourceViewSet, basename="widgetdatasource")
router.register("dashboard-shares", DashboardShareViewSet, basename="dashboardshare")

urlpatterns = router.urls
