from rest_framework import serializers

from apps.attendance.models import AttendanceRecord, OvertimeRequest, Shift, ShiftAssignment
from apps.core.mixins import TenantSerializer


class ShiftSerializer(TenantSerializer):
    class Meta:
        model = Shift
        fields = ("id", "name", "start_time", "end_time", "hours", "created_at")
        read_only_fields = ("id", "created_at")


class ShiftAssignmentSerializer(TenantSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    shift_name = serializers.CharField(source="shift.name", read_only=True)

    class Meta:
        model = ShiftAssignment
        fields = ("id", "employee", "employee_name", "shift", "shift_name", "date", "created_at")
        read_only_fields = ("id", "created_at")


class AttendanceRecordSerializer(TenantSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    employee_email = serializers.EmailField(source="employee.email", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = (
            "id",
            "employee",
            "employee_name",
            "employee_email",
            "date",
            "check_in",
            "check_out",
            "status",
            "hours_worked",
            "created_at",
        )
        read_only_fields = ("id", "hours_worked", "created_at")


class OvertimeRequestSerializer(TenantSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)

    class Meta:
        model = OvertimeRequest
        fields = ("id", "employee", "employee_name", "date", "hours", "reason", "status", "created_at")
        read_only_fields = ("id", "created_at")
