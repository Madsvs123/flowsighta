from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.timesheets.models import Timesheet, TimesheetApproval, TimesheetEntry, TimesheetPolicy
from apps.timesheets.serializers import (
    TimesheetApprovalSerializer,
    TimesheetEntrySerializer,
    TimesheetPolicySerializer,
    TimesheetSerializer,
)


class TimesheetViewSet(TenantViewSet):
    queryset = Timesheet.objects.select_related("user")
    serializer_class = TimesheetSerializer
    required_permission = "timesheets.view"
    write_permission = "timesheets.manage"
    search_fields = ["user__first_name", "user__last_name", "user__email"]
    filterset_fields = ["user", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        entries = TimesheetEntry.objects.filter(organization=request.organization)
        return Response((
            {
                "timesheet_count": qs.count(),
                "draft_count": qs.filter(status=Timesheet.Status.DRAFT).count(),
                "pending_approval": qs.filter(status=Timesheet.Status.SUBMITTED).count(),
                "approved_hours": float(
                    qs.filter(status=Timesheet.Status.SUBMITTED).aggregate(v=Sum("total_hours"))["v"] or 0
                ),
                "total_hours": float(qs.aggregate(v=Sum("total_hours"))["v"] or 0),
                "entry_count": entries.count(),
                "by_status": {s: qs.filter(status=s).count() for s, _ in Timesheet.Status.choices},
            }
        )

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        timesheet = self.get_object()
        total = timesheet.entries.aggregate(v=Sum("hours"))["v"] or 0
        timesheet.total_hours = total
        timesheet.status = Timesheet.Status.SUBMITTED
        timesheet.save(update_fields=["total_hours", "status", "updated_at"])
        return Response(self.get_serializer(timesheet).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        timesheet = self.get_object()
        timesheet.status = Timesheet.Status.APPROVED
        timesheet.save(update_fields=["status", "updated_at"])
        TimesheetApproval.objects.create(
            organization=timesheet.organization,
            timesheet=timesheet,
            approver=request.user,
            decision=TimesheetApproval.Decision.APPROVED,
            comment=request.data.get("comment", ""),
        )
        return Response(self.get_serializer(timesheet).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        timesheet = self.get_object()
        timesheet.status = Timesheet.Status.REJECTED
        timesheet.save(update_fields=["status", "updated_at"])
        TimesheetApproval.objects.create(
            organization=timesheet.organization,
            timesheet=timesheet,
            approver=request.user,
            decision=TimesheetApproval.Decision.REJECTED,
            comment=request.data.get("comment", ""),
        )
        return Response(self.get_serializer(timesheet).data)


class TimesheetEntryViewSet(TenantViewSet):
    queryset = TimesheetEntry.objects.select_related("timesheet")
    serializer_class = TimesheetEntrySerializer
    required_permission = "timesheets.view"
    write_permission = "timesheets.manage"
    search_fields = ["project_ref", "activity", "timesheet__user__first_name"]
    filterset_fields = ["timesheet", "date", "project_ref"]


class TimesheetApprovalViewSet(TenantViewSet):
    queryset = TimesheetApproval.objects.select_related("timesheet", "approver")
    serializer_class = TimesheetApprovalSerializer
    required_permission = "timesheets.view"
    write_permission = "timesheets.manage"
    http_method_names = ["get", "head", "options"]
    search_fields = ["timesheet__user__first_name", "approver__first_name"]
    filterset_fields = ["timesheet", "decision", "approver"]


class TimesheetPolicyViewSet(TenantViewSet):
    queryset = TimesheetPolicy.objects.all()
    serializer_class = TimesheetPolicySerializer
    required_permission = "timesheets.view"
    write_permission = "timesheets.manage"
    search_fields = ["name"]
    filterset_fields = ["is_active"]
