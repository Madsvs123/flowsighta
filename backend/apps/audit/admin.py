from django.contrib import admin

from apps.audit.models import AuditAction, AuditEngagement, AuditFinding, AuditProgram


@admin.register(AuditProgram)
class AuditProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "period", "status")
    list_filter = ("status",)
    search_fields = ("name", "period")


@admin.register(AuditEngagement)
class AuditEngagementAdmin(admin.ModelAdmin):
    list_display = ("scope", "program", "auditor", "start_date", "end_date", "status")
    list_filter = ("status",)
    search_fields = ("scope", "program__name")


@admin.register(AuditFinding)
class AuditFindingAdmin(admin.ModelAdmin):
    list_display = ("description", "engagement", "severity", "status")
    list_filter = ("severity", "status")
    search_fields = ("description", "engagement__scop")


@admin.register(AuditAction)
class AuditActionAdmin(admin.ModelAdmin):
    list_display = ("action", "finding", "owner", "due_date", "status")
    list_filter = ("status",)
    search_fields = ("action", "finding__description")
