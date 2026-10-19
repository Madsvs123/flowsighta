from django.contrib import admin

from apps.packing.models import Box, PackedItem, PackingSession


@admin.register(PackingSession)
class PackingSessionAdmin(admin.ModelAdmin):
    list_display = ("number", "status", "shipment", "packed_by", "created_at")
    list_filter = ("status",)
    search_fields = ("number",)


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ("code", "session", "weight", "sealed")
    list_filter = ("is_sealed",)
    search_fields = ("code", "session__number")


@admin.register(PackedItem)
class PackedItemAdmin(admin.ModelAdmin):
    list_display = ("box", "product", "quantity", "batch_number")
    search_fields = ("product__sku", "batch_number")
