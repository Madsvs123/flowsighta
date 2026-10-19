from django.contrib import admin

from apps.maintenance.models import Equipment, MaintenanceLog, MaintenanceOrder, MaintenancePlan


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "type", "location", "status", "installed_date")
    list_filter = ("status",)
    search_fields = ("code", "name")


@admin.register(MaintenancePlan)
class MaintenancePlanAdmin(admin.ModelAdmin):
    list_display = ("equipment", "type", "frequency_days", "is_active")
    list_filter = ("type", "is_active")


@admin.register(MaintenanceOrder)
class MaintenanceOrderAdmin(admin.ModelAdmin):
    list_display = ("equipment", "plan", "status", "scheduled_date", "completed_date", "cost")
    list_filter = ("status",)
    search_fields = ("equipment__code",)


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ("order", "performed_by", "hours", "created_at")
