from django.contrib import admin

from apps.shipping.models import OutboundLine, OutboundOrder, ShipmentPlan


@admin.register(OutboundOrder)
class OutboundOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "order_type", "warehouse", "status", "requested_ship_date", "created_at")
    list_filter = ("status",)
    search_fields = ("number",)


@admin.register(OutboundLine)
class OutboundLineAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "allocated_quantity", "shipped_quantity")
    search_fields = ("order__number", "product__sku")


@admin.register(ShipmentPlan)
class ShipmentPlanAdmin(admin.ModelAdmin):
    list_display = ("order", "carrier", "service", "eta", "cost", "status")
    list_filter = ("status",)
    search_fields = ("order__number", "carrier__name")
