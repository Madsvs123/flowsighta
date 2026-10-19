from django.contrib import admin

from apps.attendance.models import AttendanceRecord, OvertimeRequest, Shift, ShiftAssignment


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("name", "start_time", "end_time", "hours")


@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ("employee", "shift", "date")
    list_filter = ("shift", "date")


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "check_in", "check_out", "status", "hours_worked")
    list_filter = ("status", "date")
    search_fields = ("employee__email", "employee__first_name", "employee__lastname")


@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "hours", "status")
    list_filter = ("status",)
