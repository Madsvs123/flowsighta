from django.contrib import admin

from apps.warehousing.models import Bin, PutawayRule, StorageZone


@admin.register(StorageZone)
class StorageZoneAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "warehouse", "type")
    list_filter = ("type",)


@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ("code", "zone", "capacity", "active")
    list_filter = ("is_active",)


@admin.register(PutawayRule)
class PutawayRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "zone", "priority")
