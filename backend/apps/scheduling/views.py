from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.scheduling.models import Schedule, ScheduleConstraint, ScheduleTask
from apps.scheduling.serializers import (
    ScheduleConstraintSerializer,
    ScheduleSerializer,
    ScheduleTaskSerializer,
)
from apps.scheduling.tasks import expire_stale_schedules, release_blocked_tasks


class ScheduleViewSet(TenantViewSet):
    queryset = Schedule.objects.prefetch_related("tasks")
    serializer_class = ScheduleSerializer
    required_permission = "scheduling.view"
    write_permission = "scheduling.manage"
    search_fields = ["name"]
    filterset_fields = ["status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        tasks = ScheduleTask.objects.filter(organization=request.organization)
        return Response(
            {
                "total": qs.count(),
                "draft": qs.filter(status=Schedule.Status.DRAFT).count(),
                "published": qs.filter(status=Schedule.Status.PUBLISHED).count(),
                "locked": qs.filter(status=Schedule.Status.LOCKED).count(),
                "task_count": tasks.count(),
                "completed_tasks": tasks.filter(status=ScheduleTask.Status.COMPLETED).count(),
                "blocked_tasks": tasks.filter(status=ScheduleTask.Status.BLOCKED).count(),
                "in_progress_tasks": tasks.filter(status=ScheduleTask.Status.IN_PROGRESS).count(),
                "constraint_count": ScheduleConstraint.objects.filter(
                    organization=request.organization
                ).count(),
            }
        )

    @action(detail=False, methods=["post"])
    def refresh(self, request):
        org_id = request.organization.id
        locked = expire_stale_schedules(organization_id=org_id)
        released = release_blocked_tasks(organization_id=org_id)
        return Response({**locked, **released})

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        schedule = self.get_object()
        if schedule.status != Schedule.Status.LOCKED:
            return Response({"detail": "Locked schedules cannot be published."}, status=400)
        schedule.status = Schedule.Status.PUBLISHED
        schedule.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(schedule).data)

    @action(detail=True, methods=["post"])
    def lock(self, request, pk=None):
        schedule = self.get_object()
        schedule.status = Schedule.Status.LOCKED
        schedule.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(schedule).data)


class ScheduleTaskViewSet(TenantViewSet):
    queryset = ScheduleTask.objects.select_related("schedule")
    serializer_class = ScheduleTaskSerializer
    required_permission = "scheduling.view"
    write_permission = "scheduling.manage"
    search_fields = ["reference", "resource", "schedule__name"]
    filterset_fields = ["schedule", "resource", "status"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = ScheduleTask.Status.COMPLETED
        task.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def block(self, request, pk=None):
        task = self.get_object()
        task.status = ScheduleTask.Status.BLOCKED
        task.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(task).data)


class ScheduleConstraintViewSet(TenantViewSet):
    queryset = ScheduleConstraint.objects.select_related("task")
    serializer_class = ScheduleConstraintSerializer
    required_permission = "scheduling.view"
    write_permission = "scheduling.manage"
    search_fields = ["task__reference"]
    filterset_fields = ["task", "type"]
