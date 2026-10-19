from django.contrib import admin

from apps.resources.models import Resource, ResourceAllocation, ResourceCalendar, ResourceSkill


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "cost_rate", "status")
    list_filter = ("type", "status")
    search_fields = ("name",)


@admin.register(ResourceSkill)
class ResourceSkillAdmin(admin.ModelAdmin):
    list_display = ("resource", "skill", "level")
    list_filter = ("level",)
    search_fields = ("skill", "resource__name")


@admin.register(ResourceAllocation)
class ResourceAllocationAdmin(admin.ModelAdmin):
    list_display = ("resource", "project_ref", "start_date", "end_date", "hours_per_week", "status")
    list_filter = ("status",)
    search_fields = ("project_ref", "resource__name")


@admin.register(ResourceCalendar)
class ResourceCalendarAdmin(admin.ModelAdmin):
    list_display = ("resource", "date", "available_hour")
    list_filter = ("date",)
