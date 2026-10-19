from django.contrib import admin

from apps.workflows.models import WorkflowAudit, WorkflowDefinition, WorkflowInstance, WorkflowStep


@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "trigger", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("name", "trigger")


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ("definition", "status", "started_at", "finished_at")
    list_filter = ("status",)
    search_fields = ("definition__name",)


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ("instance", "name", "status")
    list_filter = ("status",)
    search_fields = ("name", "instance__definition__name")


@admin.register(WorkflowAudit)
class WorkflowAuditAdmin(admin.ModelAdmin):
    list_display = ("instance", "event", "occurred_at")
    search_fields = ("event", "instance__definition__name")
