from django.contrib import admin

from apps.sourcing.models import SourcingAward, SourcingBid, SourcingEvent, SourcingLine


@admin.register(SourcingEvent)
class SourcingEventAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "type", "status", "opens_at", "closes_at")
    list_filter = ("type", "status")
    search_fields = ("number", "title")


@admin.register(SourcingLine)
class SourcingLineAdmin(admin.ModelAdmin):
    list_display = ("event", "product", "quantity", "target_price")
    list_filter = ("event__status",)
    search_fields = ("event__number", "product__sku")


@admin.register(SourcingBid)
class SourcingBidAdmin(admin.ModelAdmin):
    list_display = ("line", "supplier", "amount", "incoterm", "delivery_days", "is_winner")
    list_filter = ("is_winner", "incoterm")
    search_fields = ("supplier__name", "line__event__number")


@admin.register(SourcingAward)
class SourcingAwardAdmin(admin.ModelAdmin):
    list_display = ("event", "bid", "awarded_at")
    list_filter = ("event__status",)
    search_fields = ("event__title", "bid__supplier__name")
