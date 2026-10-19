from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.core.services import next_number
from apps.picking.models import PickLine, PickTask, PickWave
from apps.picking.serializers import PickLineSerializer, PickTaskSerializer, PickWaveSerializer


class PickWaveViewSet(TenantViewSet):
    queryset = PickWave.objects.select_related("warehouse")
    serializer_class = PickWaveSerializer
    required_permission = "picking.view"
    write_permission = "picking.manage"
    search_fields = ["number", "warehouse__code"]
    filterset_fields = ["warehouse", "status", "priority"]

    def perform_create(self, serializer):
        instance = serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        if not instance.number:
            instance.number = next_number(PickWave, instance.organization, "WAV")
            instance.save(update_fields=["number"])

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        lines = PickLine.objects.filter(wave__organization_id=request.organization.id)
        tasks = PickTask.objects.filter(wave__organization_id=request.organization.id)
        return Response(
            {
                "wave_count": qs.count(),
                "created": qs.filter(status=PickWave.Status.CREATED).count(),
                "released": qs.filter(status=PickWave.Status.RELEASED).count(),
                "in_progress": qs.filter(status=PickWave.Status.IN_PROGRESS).count(),
                "completed": qs.filter(status=PickWave.Status.COMPLETED).count(),
                "line_count": lines.count(),
                "lines_pending": lines.filter(status=PickLine.Status.PENDING).count(),
                "lines_picked": lines.filter(status=PickLine.Status.PICKED).count(),
                "tasks_pending": tasks.filter(status=PickTask.Status.PENDING).count(),
                "by_status": [
                    {"status": s, "count": qs.filter(status=s).count()}
                    for s in PickWave.Status.values
                ],
            }
        )

    @action(detail=True, methods=["post"])
    def release(self, request, pk=None):
        wave = self.get_object()
        if wave.status != PickWave.Status.CREATED:
            return Response({"detail": "Only created waves can be released."}, status=400)
        wave.status = PickWave.Status.IN_PROGRESS
        wave.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(wave).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        wave = self.get_object()
        if wave.status in (PickWave.Status.COMPLETED, PickWave.Status.CANCELLED):
            return Response({"detail": "Wave is already closed."}, status=400)
        wave.status = PickWave.Status.COMPLETED
        wave.save(update_fields=["status", "updated_at"])
        wave.lines.update(status=PickLine.Status.PICKED)
        wave.tasks.update(status=PickTask.Status.COMPLETED, completed_at=timezone.now())
        return Response(self.get_serializer(wave).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        wave = self.get_object()
        if wave.status == PickWave.Status.COMPLETED:
            return Response({"detail": "Completed waves cannot be cancelled."}, status=400)
        wave.status = PickWave.Status.CANCELLED
        wave.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(wave).data)


class PickLineViewSet(TenantViewSet):
    queryset = PickLine.objects.select_related("wave", "product")
    serializer_class = PickLineSerializer
    required_permission = "picking.view"
    write_permission = "picking.manage"
    search_fields = ["wave__number", "product__sku", "from_bin"]
    filterset_fields = ["wave", "product", "status"]

    @action(detail=True, methods=["post"])
    def pick(self, request, pk=None):
        line = self.get_object()
        line.status = PickLine.Status.PICKED
        line.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(line).data)


class PickTaskViewSet(TenantViewSet):
    queryset = PickTask.objects.select_related("wave", "assignee")
    serializer_class = PickTaskSerializer
    required_permission = "picking.view"
    write_permission = "picking.manage"
    search_fields = ["wave__number"]
    filterset_fields = ["wave", "assignee", "status"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = PickTask.Status.COMPLETED
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at", "updated_at"])
        return Response(self.get_serializer(task).data)
