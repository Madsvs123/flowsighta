from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.attendance.models import AttendanceRecord, OvertimeRequest, Shift, ShiftAssignment
from apps.attendance.serializers import (
    AttendanceRecordSerializer,
    OvertimeRequestSerializer,
    ShiftAssignmentSerializer,
    ShiftSerializer,
)
from apps.core.mixins import TenantViewSet


class ShiftViewSet(TenantViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    required_permission = "attendance.view"
    write_permission = "attendance.manage"
    search_fields = ["name"]


class ShiftAssignmentViewSet(TenantViewSet):
    queryset = ShiftAssignment.objects.select_related("employee", "shift")
    serializer_class = ShiftAssignmentSerializer
    required_permission = "attendance.view"
    write_permission = "attendance.manage"
    search_fields = ["employee__first_name", "employee__last_name", "shift__name"]
    filterset_fields = ["employee", "shift", "date"]


class AttendanceRecordViewSet(TenantViewSet):
    queryset = AttendanceRecord.objects.select_related("employee")
    serializer_class = AttendanceRecordSerializer
    required_permission = "attendance.view"
    write_permission = "attendance.manage"
    search_fields = ["employee__first_name", "employee__last_name", "employee__email"]
    filterset_fields = ["employee", "date", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = {label: qs.filter(status=value).count() for value, label in AttendanceRecord.Status.choices}
        totals = qs.aggregate(total_hours=Sum("hours_worked"))
        today = timezone.now().date()
        return Response(
            {
                "total_records": qs.count(),
                "by_status": by_status,
                "total_hours": float(totals["total_hours"] or 0),
                "today_records": qs.filter(date=today).count(),
                "today_hours": float(qs.filter(date=today).aggregate(total=Sum("hours_worked"))["total"] or 0),
            }
        )

    @action(detail=True, methods=["post"])
    def checkout(self, request, pk=None):
        record = self.get_object()
        check_out = request.data.get("check_out")
        if check_out:
            record.check_out = check_out
            if record.check_in:
                delta = timezone.datetime.combine(record.date, record.check_out) - timezone.datetime.combine(
                    record.date, record.check_in
                )
                record.hours_worked = Decimal(str(max(delta.total_seconds() / 3600, 0))).quantize(Decimal("0.01"))
        record.status = AttendanceRecord.Status.PRESENT
        record.save(update_fields=["check_out", "hours_worked", "status", "updated_at"])
        return Response(self.get_serializer(record).data)


class OvertimeRequestViewSet(TenantViewSet):
    queryset = OvertimeRequest.objects.select_related("employee")
    serializer_class = OvertimeRequestSerializer
    required_permission = "attendance.view"
    write_permission = "attendance.manage"
    search_fields = ["employee__first_name", "employee__last_name", "reason"]
    filterset_fields = ["employee", "status"]

    def _decide(self, request, pk, status):
        overtime = self.get_object()
        if overtime.status != OvertimeRequest.Status.APPROVED:
            return Response({"detail": "Only pending requests can be decided"}, status=400)
        overtime.status = status
        overtime.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(overtime).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._decide(request, pk, OvertimeRequest.Status.APPROVED)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._decide(request, pk, OvertimeRequest.Status.REJECTED)
