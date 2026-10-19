from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.reporting.models import Report, ReportRun, ReportSchedule, ReportTemplate
from apps.reporting.serializers import (
    ReportRunSerializer,
    ReportScheduleSerializer,
    ReportSerializer,
    ReportTemplateSerializer,
)


class ReportViewSet(TenantViewSet):
    queryset = Report.objects.select_related("created_by").annotate(run_count=Count("runs"))
    serializer_class = ReportSerializer
    required_permission = "reporting.view"
    write_permission = "reporting.manage"
    search_fields = ["name"]
    filterset_fields = ["type", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        reports = self.get_queryset()
        runs = ReportRun.objects.filter(organization=request.organization)
        schedules = ReportSchedule.objects.filter(organization=request.organization)
        return Response(
            {
                "report_count": reports.count(),
                "published_reports": reports.filter(status=Report.Status.PUBLISHED).count(),
                "draft_reports": reports.filter(status=Report.Status.DRAFT).count(),
                "archived_reports": reports.filter(status=Report.Status.ARCHIVED).count(),
                "total_runs": runs.count(),
                "completed_runs": runs.filter(status=ReportRun.Status.COMPLETED).count(),
                "failed_runs": runs.filter(status=ReportRun.Status.FAILED).count(),
                "active_schedules": schedules.filter(is_active=True).count(),
                "template_count": ReportTemplate.objects.filter(organization=request.organization).count(),
                "reports_by_type": {
                    label: reports.filter(type=t).count() for t, label in Report.Type.choices
                },
            }
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        report = self.get_object()
        report.status = Report.Status.PUBLISHED
        report.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(report).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        report = self.get_object()
        report.status = Report.Status.ARCHIVED
        report.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(report).data)


class ReportScheduleViewSet(TenantViewSet):
    queryset = ReportSchedule.objects.select_related("report")
    serializer_class = ReportScheduleSerializer
    required_permission = "reporting.view"
    write_permission = "reporting.manage"
    search_fields = ["report__name", "cron"]
    filterset_fields = ["report", "is_active"]

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(schedule).data)


class ReportRunViewSet(TenantViewSet):
    queryset = ReportRun.objects.select_related("report")
    serializer_class = ReportRunSerializer
    required_permission = "reporting.view"
    write_permission = "reporting.manage"
    search_fields = ["report__name", "output_ref"]
    filterset_fields = ["report", "status"]

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        run = self.get_object()
        if run.status in (ReportRun.Status.RUNNING, ReportRun.Status.FAILED):
            return Response({"detail": "Run already executed"}, status=400)
        run.status = ReportRun.Status.RUNNING
        run.started_at = timezone.now()
        run.save(update_fields=["status", "started_at", "updated_at"])
        run.status = ReportRun.Status.COMPLETED
        run.finished_at = timezone.now()
        run.output_ref = f"reports/{run.report_id}/{run.pk}.json"
        run.save(update_fields=["status", "finished_at", "output_ref", "updated_at"])
        return Response(self.get_serializer(run).data)


class ReportTemplateViewSet(TenantViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    required_permission = "reporting.view"
    write_permission = "reporting.manage"
    search_fields = ["name", "category"]
    filterset_fields = ["category", "is_active"]
