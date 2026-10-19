from django.contrib import admin

from apps.projects.models import Project, ProjectMember, ProjectMilestone, ProjectTask


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "status", "manager", "budget", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("cod", "name")


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "role")
    search_fields = ("project__code", "user__email")


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "assignee", "due_date")
    list_filter = ("status", "priority")
    search_fields = ("title", "project__code")


@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "date", "status")
    list_filter = ("status",)
    search_fields = ("title", "project__code")
