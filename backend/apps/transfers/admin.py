from django.contrib import admin

from apps.transfers.models import TransferLine, TransferOrder, TransferShipment


@admin.register(TransferOrder)
class TransferOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "from_warehouse", "to_warehouse", "status", "requested_by")
    list_filter = ("status",)
    readonly_fields = ("number",)


@admin.register(TransferLine)
class TransferLineAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "shipped_quantity", "received_quantity")


@admin.register(TransferShipment)
class TransferShipmentAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "carrier", "tracking_number", "shipped_at", "delivered_at")
    list_filter = ("status",)
