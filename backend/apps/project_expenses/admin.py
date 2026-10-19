from django.contrib import admin

from apps.project_expenses.models import (
    ExpenseApproval,
    ExpenseBudget,
    ProjectBilling,
    ProjectExpense,
)


@admin.register(ProjectExpense)
class ProjectExpenseAdmin(admin.ModelAdmin):
    list_display = ("project_ref", "category", "date", "amount", "status")
    list_filter = ("status", "category")
    search_fields = ("project_ref", "description", "vendor_ref")


@admin.register(ExpenseBudget)
class ExpenseBudgetAdmin(admin.ModelAdmin):
    list_display = ("project_ref", "category", "planned_amount")
    search_fields = ("project_ref",)


@admin.register(ExpenseApproval)
class ExpenseApprovalAdmin(admin.ModelAdmin):
    list_display = ("expense", "approver", "decision", "decided_at")
    list_filter = ("decision",)


@admin.register(ProjectBilling)
class ProjectBillingAdmin(admin.ModelAdmin):
    list_display = ("project_ref", "billing_date", "amount", "currency")
    list_filter = ("status",)
    search_fields = ("project_ref",)
