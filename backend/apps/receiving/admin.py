from django.contrib import admin

from apps.receiving.models import PutawayTask, Receipt, ReceiptLine


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("number", "supplier", "warehouse", "status", "created_at")
    list_filter = ("status",)


@admin.register(ReceiptLine)
class ReceiptLineAdmin(admin.ModelAdmin):
    list_display = ("receipt", "product", "quantity", "received_quantity", "batch_number")
    list_filter = ("receipt__status",)


@admin.register(PutawayTask)
class PutawayTaskAdmin(admin.ModelAdmin):
    list_display = ("receipt_line", "bin", "status", "assigned_to")
    list_filter = ("status",)
