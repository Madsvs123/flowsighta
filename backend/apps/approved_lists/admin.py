from django.contrib import admin

from apps.approved_lists.models import ApprovedList, ApprovedSupplier


@admin.register(ApprovedList)
class ApprovedListAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "status", "description")
    list_filter = ("status", "category")
    search_fields = ("name", "category")


@admin.register(ApprovedSupplier)
class ApprovedSupplierAdmin(admin.ModelAdmin):
    list_display = ("list", "supplier", "rating", "status", "approved_date")
    list_filter = ("status",)
    search_fields = ("supplier__name", "list__name")
