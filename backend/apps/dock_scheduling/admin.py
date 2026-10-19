from django.contrib import admin

from apps.dock_scheduling.models import Dock, DockAppointment


@admin.register(Dock)
class DockAdmin(admin.ModelAdmin):
    list_display = ("code", "warehouse", "type", "is_active")
    list_filter = ("type", "is_active")
    search_fields = ("code", "warehouse__name")


@admin.register(DockAppointment)
class DockAppointmentAdmin(admin.ModelAdmin):
    list_display = ("dock", "reference", "carrier", "vehicle", "window_start", "window_end", "status")
    list_filter = ("status",)
    search_fields = ("reference", "carrier", "vehicle", "driver")
