from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.projects.models import Project, ProjectMember, ProjectMilestone, ProjectTask
from apps.projects.serializers import (
    ProjectMemberSerializer,
    ProjectMilestoneSerializer,
    ProjectSerializer,
    ProjectTaskSerializer,
)


class ProjectViewSet(TenantViewSet):
    queryset = Project.objects.select_related("manager")
    serializer_class = ProjectSerializer
    required_permission = "projects.view"
    write_permission = "projects.manage"
    search_fields = ["code", "name", "description"]
    filterset_fields = ["status", "manager"]

    @action(detail=False, methods=["get"])
    def summary(self, request)
        qs = self.get_queryset()
        tasks = ProjectTask.objects.filter(organization=request.organization)
        milestones = ProjectMilestone.objects.filter(organization=request.organization)
        today = timezone.now().date()
        return Response(
            {
                "project_count": qs.count(),
                "active_projects": qs.filter(status=Project.Status.ACTIVE).count(),
                "total_budget": float(qs.aggregate(v=Sum("budget"))["v"] or 0),
                "open_tasks": tasks.exclude(status=ProjectTask.Status.DONE).count(),
                "overdue_tasks": tasks.filter(
                    status__in=[ProjectTask.Status.TODO, ProjectTask.Status.IN_PROGRESS, ProjectTask.Status.BLOCKED],
                    due_date__lt=today,
                ).count(),
                "milestones": milestones.count(),
                "achieved_milestones": milestones.filter(status=ProjectMilestone.Status.ACHIEVED).count(),
                "by_status": {s: qs.filter(status=s).count() for s, _ in Project.Status.choices},
            }
        )

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        project = self.get_object()
        project.status = Project.Status.ACTIVE
        if not project.start_date:
            project.start_date = timezone.now().date()
        project.save(update_fields=["status", "start_date", "updated_at"])
        return Response(self.get_serializer(project).data)

    @action(detail=True, methods=["post"])
    def hold(self, request, pk=None):
        project = self.get_object()
        project.status = Project.Status.ON_HOLD
        project.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(project).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        project = self.get_object()
        project.status = Project.Status.COMPLETED
        if not project.end_date:
            project.end_date = timezone.now().date()
        project.save(update_fields=["status", "end_date", "updated_at"])
        project.tasks.filter(status=ProjectTask.Status.DONE).update(status=ProjectTask.Status.DONE)
        return Response(self.get_serializer(project).data)


class ProjectMemberViewSet(TenantViewSet):
    queryset = ProjectMember.objects.select_related("project", "user")
    serializer_class = ProjectMemberSerializer
    required_permission = "projects.view"
    write_permission = "projects.manage"
    search_fields = ["project__code", "user__first_name", "user__last_name", "role"]
    filterset_fields = ["project", "user"]


class ProjectTaskViewSet(TenantViewSet):
    queryset = ProjectTask.objects.select_related("project", "assignee")
    serializer_class = ProjectTaskSerializer
    required_permission = "projects.view"
    write_permission = "projects.manage"
    search_fields = ["title", "project__code", "assignee__first_name"]
    filterset_fields = ["project", "status", "priority", "assignee"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = ProjectTask.Status.DONE
        task.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(task).data)


class ProjectMilestoneViewSet(TenantViewSet):
    queryset = ProjectMilestone.objects.select_related("project")
    serializer_class = ProjectMilestoneSerializer
    required_permission = "projects.view"
    write_permission = "projects.manage"
    search_fields = ["title", "project__code"]
    filterset_fields = ["project", "status"]

    @action(detail=True, methods=["post"])
    def mark_achieved(self, request, pk=None):
        milestone = self.get_object()
        milestone.status = ProjectMilestone.Status.ACHIEVED
        milestone.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(milestone).data)
