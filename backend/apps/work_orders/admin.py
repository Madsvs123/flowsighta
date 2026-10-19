from django.contrib import admin

from apps.work_orders.models import WorkOrder, WorkOrderLabor, WorkOrderTask


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "type", "status", "priority", "assigned_to", "due_date")
    list_filter = ("status", "type", "priority")
    search_fields = ("number",)


@admin.register(WorkOrderTask)
class WorkOrderTaskAdmin(admin.ModelAdmin):
    list_display = ("order", "description", "status", "duration")
    list_filter = ("status",)


@admin.register(WorkOrderLabor)
class WorkOrderLaborAdmin(admin.ModelAdmin):
    list_display = ("order", "user", "hours", "date")
