from django.contrib import admin

from apps.yard.models import YardGateLog, YardLocation, YardMove


@admin.register(YardLocation)
class YardLocationAdmin(admin.ModelAdmin):
    list_display = ("code", "warehouse", "type", "is_active")
    list_filter = ("type", "is_active")
    search_fields = ("code", "warehouse__name")


@admin.register(YardMove)
class YardMoveAdmin(admin.ModelAdmin):
    list_display = ("location", "vehicle", "trailer", "direction", "status", "moved_at")
    list_filter = ("status", "direction")
    search_fields = ("vehicle", "trailer", "location")


@admin.register(YardGateLog)
class YardGateLogAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "trailer", "direction", "driver", "gate", "occurred_at")
    list_filter = ("direction",)
    search_fields = ("vehicle", "trailer", "driver", "gate")
