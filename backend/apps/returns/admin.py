from django.contrib import admin

from apps.returns.models import RestockTask, ReturnLine, ReturnOrder


@admin.register(ReturnOrder)
class ReturnOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "type", "status", "reference", "created_by", "created_at")
    list_filter = ("status", "type")
    search_fields = ("number", "reference")


@admin.register(ReturnLine)
class ReturnLineAdmin(admin.ModelAdmin):
    list_display = ("order", "product__name", "quantity", "condition", "disposition")
    list_filter = ("condition", "disposition")
    search_fields = ("order__number", "product__sku")


@admin.register(RestockTask)
class RestockTaskAdmin(admin.ModelAdmin):
    list_display = ("line", "warehouse", "bin", "status")
    list_filter = ("status",)
    search_fields = ("line__order__number", "bin")
