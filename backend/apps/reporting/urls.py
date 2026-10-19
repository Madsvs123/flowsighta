from rest_framework.routers import DefaultRouter

from apps.reporting.views import (
    ReportRunViewSet,
    ReportScheduleViewSet,
    ReportTemplateViewSet,
    ReportViewSet,
)

router = DefaultRouter()
router.register("reporting", ReportViewSet, basename="report")
router.register("report-schedules", ReportScheduleViewSet, basename="reportschedule")
router.register("report-runs", ReportRunViewSet, basename="reportrun")
router.register("report-templates", ReportTemplateViewSet, basename="report-template")

urlpatterns = router.urls
