from django.contrib import admin

from apps.leave.models import LeaveApproval, LeaveBalance, LeavePolicy, LeaveRequest


@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "days_per_year", "carryover_days", "is_active")
    list_filter = ("type", "is_active")


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "policy", "year", "allocated", "used", "remain")
    list_filter = ("year", "policy")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "policy", "start_date", "end_date", "days", "status")
    list_filter = ("status", "policy")
    search_fields = ("employee__email", "employee__first_name", "employee__last_name")


@admin.register(LeaveApproval)
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ("request", "approver", "decision", "decided_at")
    list_filter = ("decision",)
