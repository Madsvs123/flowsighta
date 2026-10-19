from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.timesheets.models import Timesheet, TimesheetApproval, TimesheetEntry, TimesheetPolicy


class TimesheetSerializer(TenantSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Timesheet
        fields = (
            "id",
            "user",
            "user_name",
            "period_start",
            "period_end",
            "status",
            "total_hours",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class TimesheetEntrySerializer(TenantSerializer):
    timesheet_status = serializers.CharField(source="timesheet.status", read_only=True)

    class Meta:
        model = TimesheetEntry
        fields = (
            "id",
            "timesheet",
            "timesheet_status",
            "date",
            "project_ref",
            "activity",
            "hours",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class TimesheetApprovalSerializer(TenantSerializer):
    timesheet_status = serializers.CharField(source="timesheet.status", read_only=True)
    approver_name = serializers.CharField(source="approver.get_full_name", read_only=True)

    class Meta:
        model = TimesheetApproval
        fields = (
            "id",
            "timesheet",
            "timesheet_status",
            "approver",
            "approver_name",
            "decision",
            "comment",
            "decided_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class TimesheetPolicySerializer(TenantSerializer):
    class Meta:
        model = TimesheetPolicy
        fields = ("id", "name", "hours_per_day", "is_active", "created_at")
        read_only_fields = ("id", "created_at")
