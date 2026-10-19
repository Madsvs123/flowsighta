from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.reporting.models import Report, ReportRun, ReportSchedule, ReportTemplate


class ReportSerializer(TenantSerializer):
    run_count = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = Report
        fields = (
            "id",
            "name",
            "type",
            "config",
            "status",
            "run_count",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ReportScheduleSerializer(TenantSerializer):
    report_name = serializers.CharField(source="report.name", read_only=True)

    class Meta:
        model = ReportSchedule
        fields = (
            "id",
            "report",
            "report_name",
            "cron",
            "recipients",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ReportRunSerializer(TenantSerializer):
    report_name = serializers.CharField(source="report.name", read_only=True)

    class Meta:
        model = ReportRun
        fields = (
            "id",
            "report",
            "report_name",
            "status",
            "started_at",
            "finished_at",
            "output_ref",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "started_at", "finished_at", "output_ref", "created_at", "updated_at")


class ReportTemplateSerializer(TenantSerializer):
    class Meta:
        model = ReportTemplate
        fields = ("id", "name", "category", "schema", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
