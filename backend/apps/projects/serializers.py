from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.projects.models import Project, ProjectMember, ProjectMilestone, ProjectTask


class ProjectSerializer(TenantSerializer):
    manager_name = serializers.CharField(source="manager.get_full_name", read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "code",
            "name",
            "description",
            "status",
            "start_date",
            "end_date",
            "manager",
            "manager_name",
            "budget",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ProjectMemberSerializer(TenantSerializer):
    project_code = serializers.CharField(source="project.code", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = ProjectMember
        fields = (
            "id",
            "project",
            "project_code",
            "project_name",
            "user",
            "user_name",
            "role",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "role")


class ProjectTaskSerializer(TenantSerializer):
    project_code = serializers.CharField(source="project.code", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    assignee_name = serializers.CharField(source="assignee.get_full_name", read_only=True)

    class Meta:
        model = ProjectTask
        fields = (
            "id",
            "project",
            "project_code",
            "project_name",
            "title",
            "status",
            "assignee",
            "assignee_name",
            "created_at",
            "priority",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ProjectMilestoneSerializer(TenantSerializer):
    project_code = serializers.CharField(source="project.code", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = ProjectMilestone
        fields = (
            "id",
            "project",
            "project_code",
            "project_name",
            "title",
            "date",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
