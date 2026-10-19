from django.contrib import admin

from apps.sales_orders.models import OrderAllocation, SalesOrder, SalesOrderLine, SalesShipment


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "customer_ref", "status", "total", "currency", "order_date")
    list_filter = ("status", "currency")
    search_fields = ("number", "customer_ref")


@admin.register(SalesOrderLine)
class SalesOrderLineAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "unit_price", "line_total")
    search_fields = ("order__number", "product__name")


@admin.register(OrderAllocation)
class OrderAllocationAdmin(admin.ModelAdmin):
    list_display = ("line", "stock_item", "quantity")


@admin.register(SalesShipment)
class SalesShipmentAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "tracking_number", "shipped_at")
    list_filter = ("status",)
