from django.contrib import admin

from apps.reporting.models import Report, ReportRun, ReportSchedule, ReportTemplate


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "status", "created_at")
    list_filter = ("type", "status")
    search_fields = ("name",)


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ("report", "cron", "is_active")
    list_filter = ("is_active",)
    search_fields = ("report__name", "cron")


@admin.register(ReportRun)
class ReportRunAdmin(admin.ModelAdmin):
    list_display = ("report", "status", "started_at", "finished_at")
    list_filter = ("status",)
    search_fields = ("report__name", "output")


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
