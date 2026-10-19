from django.contrib import admin

from apps.cycle_counts.models import CountLine, CycleCount


@admin.register(CycleCount)
class CycleCountAdmin(admin.ModelAdmin):
    list_display = ("number", "warehouse", "type", "status", "scheduled_on", "counted_by")
    list_filter = ("status",)


@admin.register(CountLine)
class CountLineAdmin(admin.ModelAdmin):
    list_display = ("count", "product", "bin", "system_qty", "counted_qty", "variance", "status")
    list_filter = ("status",)
