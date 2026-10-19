from django.contrib import admin

from apps.pricing.models import Discount, PriceChange, PriceList, PriceListItem


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ("name", "currency", "is_default", "status")
    list_filter = ("status", "is_default", "currency")
    search_fields = ("currency",)


@admin.register(PriceListItem)
class PriceListItemAdmin(admin.ModelAdmin):
    list_display = ("price_list", "product", "price", "min_quantity")
    search_fields = ("product__sku", "price_list__name")


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "value", "status", "valid_from", "valid_to")
    list_filter = ("type", "status")


@admin.register(PriceChange)
class PriceChangeAdmin(admin.ModelAdmin):
    list_display = ("product", "old_price", "new_price", "reason", "changed_by")
    search_fields = ("product__sku", "reason")
