from django.contrib import admin

from apps.expenses.models import ExpenseApproval, ExpenseLine, ExpenseReport, Reimbursement


@admin.register(ExpenseReport)
class ExpenseReportAdmin(admin.ModelAdmin):
    list_display = ("number", "employee", "status", "total")
    list_filter = ("status",)
    search_fields = ("number", "employee__email")


@admin.register(ExpenseLine)
class ExpenseLineAdmin(admin.ModelAdmin):
    list_display = ("report", "category", "date", "description", "amount")
    list_filter = ("category",)
    search_fields = ("report__number", "description")


@admin.register(ExpenseApproval)
class ExpenseApprovalAdmin(admin.ModelAdmin):
    list_display = ("report", "approver", "decision", "decided_at")
    list_filter = ("decision",)


@admin.register(Reimbursement)
class ReimbursementAdmin(admin.ModelAdmin):
    list_display = ("report", "payment_reference", "amount", "paid_at")
