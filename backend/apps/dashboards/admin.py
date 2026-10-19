from django.contrib import admin

from apps.dashboards.models import Dashboard, DashboardShare, DashboardWidget, WidgetDataSource


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default", "owner", "updated_at")
    list_filter = ("is_default",)
    search_fields = ("name", "owner__email")


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ("dashboard", "type", "created_at")
    list_filter = ("type",)
    search_fields = ("dashboard__name",)


@admin.register(WidgetDataSource)
class WidgetDataSourceAdmin(admin.ModelAdmin):
    list_display = ("widget", "source_ref")
    search_fields = ("source_ref", "widget__dashboard__name")


@admin.register(DashboardShare)
class DashboardShareAdmin(admin.ModelAdmin):
    list_display = ("dashboard", "user", "role")
    list_filter = ("role",)
    search_fields = ("dashboard__name", "user__email")
