from django.contrib import admin

from apps.employees.models import Department, Employee, EmploymentHistory


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "manager", "is_active")
    search_fields = ("code", "name")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_no", "user", "job_title", "department", "status", "hired_date")
    list_filter = ("status", "department")
    search_fields = ("employee_no", "user__email", "user__first_name", "user__last_name")


@admin.register(EmploymentHistory)
class EmploymentHistoryAdmin(admin.ModelAdmin):
    list_display = ("employee", "position", "department", "start_date", "end_date")
    search_fields = ("position", "employee__user__email")
