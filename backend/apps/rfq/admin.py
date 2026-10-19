from django.contrib import admin

from apps.rfq.models import Rfq, RfqLine, RfqResponse, RfqResponseLine


@admin.register(Rfq)
class RfqAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "status", "due_date")
    list_filter = ("status",)
    search_fields = ("number", "title")


@admin.register(RfqLine)
class RfqLineAdmin(admin.ModelAdmin):
    list_display = ("rfq", "product", "quantity", "target_price")
    search_fields = ("rfq__number", "sku")


@admin.register(RfqResponse)
class RfqResponseAdmin(admin.ModelAdmin):
    list_display = ("rfq", "supplier", "status", "submitted_at")
    list_filter = ("status",)
    search_fields = ("rfq__number", "supplier__name")


@admin.register(RfqResponseLine)
class RfqResponseLineAdmin(admin.ModelAdmin):
    list_display = ("response", "product", "quantity", "unit_price", "delivery_days")
    search_fields = ("response__rfq__number", "product__sku")
