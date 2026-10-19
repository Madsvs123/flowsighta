from django.contrib import admin

from apps.payroll.models import PayrollReport, PayrollRun, Payslip, SalaryComponent


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "amount", "is_recurring", "is_active")
    list_filter = ("type", "is_active")


@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ("number", "period_start", "period_start", "status", "processed_at")
    list_filter = ("status",)


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ("run", "employee", "gross", "total_deductions", "net", "status")
    list_filter = ("status", "run")
    search_fields = ("employee__email", "employee__first_name", "employee__last_name")


@admin.register(PayrollReport)
class PayrollReportAdmin(admin.ModelAdmin):
    list_display = ("run", "created_at")
