from django.contrib import admin

from apps.picking.models import PickLine, PickTask, PickWave


@admin.register(PickWave)
class PickWaveAdmin(admin.ModelAdmin):
    list_display = ("number", "warehouse", "status", "priority", "created_at")
    list_filter = ("status", "priority")


@admin.register(PickLine)
class PickLineAdmin(admin.ModelAdmin):
    list_display = ("wave", "product", "quantity", "from_bin", "status")
    list_filter = ("status",)


@admin.register(PickTask)
class PickTaskAdmin(admin.ModelAdmin):
    list_display = ("wave", "assignee", "status", "wave")
    list_filter = ("status",)
