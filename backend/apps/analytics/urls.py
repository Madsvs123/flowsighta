from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.analytics.views import ReportJobViewSet, ScorecardSnapshotViewSet, analytics_view, dashboard_view

router = DefaultRouter()
router.register("reports", ReportJobViewSet, basename="reports")
router.register("scorecards", ScorecardSnapshotViewSet, basename="scorecards")

urlpatterns = [
    path("dashboard/", dashboard_view, name="dashboard"),
    path("analytics-data/", dashboard_view, name="analytics"),
] + router.urls
