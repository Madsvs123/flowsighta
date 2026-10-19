from django.contrib import admin

from apps.contracts.models import Contract, ContractClause, ContractTemplates


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "supplier", "type", "status", "start_date", "end_date", "total_value")
    list_filter = ("type", "status")
    search_fields = ("number", "title", "supplier__name")


@admin.register(ContractClause)
class ContractClauseAdmin(admin.ModelAdmin):
    list_display = ("contract", "title", "sort_order")
    list_filter = ("contract__status",)
    search_fields = ("title", "contract__number")


@admin.register(ContractMilestone)
class ContractMilestoneAdmin(admin.ModelAdmin):
    list_display = ("contract", "title", "due_date", "status")
    list_filter = ("status",)
    search_fields = ("title", "contract__number")
