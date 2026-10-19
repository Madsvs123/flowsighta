from django.contrib import admin

from apps.timesheets.models import Timesheet, TimesheetApproval, TimesheetEntry, TimesheetPolicy


@admin.register(TimesheetPolicy)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ("user", "period_start", "period_end", "status", "total_hours")
    list_filter = ("status",)
    search_fields = ("user__email",)


@admin.register(TimesheetEntry)
class TimesheetEntryAdmin(admin.ModelAdmin):
    list_display = ("timesheet", "date", "project_ref", "activity", "hours")
    list_filter = ("date",)
    search_fields = ("project_ref", "activity")


@admin.register(TimesheetApproval)
class TimesheetApprovalAdmin(admin.ModelAdmin):
    list_display = ("timesheet", "approver", "decision", "decided_at")
    list_filter = ("decision",)


@admin.register(Timesheet)
class TimesheetPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "hours_per_day", "overtime_rule", "is_active")
    list_filter = ("is_active",)
