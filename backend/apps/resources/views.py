from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.resources.models import Resource, ResourceAllocation, ResourceCalendar, ResourceSkill
from apps.resources.serializers import (
    ResourceAllocationSerializer,
    ResourceCalendarSerializer,
    ResourceSerializer,
    ResourceSkillSerializer,
)


class ResourceViewSet(TenantViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    required_permission = "resources.view"
    write_permission = "resources.manage"
    search_fields = ["name"]
    filterset_fields = ["type", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        allocations = ResourceAllocation.objects.filter(organization=request.organization)
        return Response(
            {
                "resource_count": qs.count(),
                "available": qs.filter(status=Resource.Status.AVAILABLE).count(),
                "allocated": qs.filter(status=Resource.Status.ALLOCATED).count(),
                "active_allocations": allocations.exclude(status=ResourceAllocation.Status.DONE).count(),
                "planned_hours": float(
                    allocations.filter(status=ResourceAllocation.Status.PLANNED).aggregate(v=Sum("hours_per_week"))[
                        "v"
                    ]
                    or 0
                ),
                "skills": ResourceSkill.objects.filter(organization=request.organization).count(),
                "by_type": {t: qs.filter(type=t).count() for t, _ in Resource.Type.choices},
                "by_status": {s: qs.filter(status=s).count() for s, _ in Resource.Status.choices},
            }
        )

    @action(detail=True, methods=["post"])
    def set_available(self, request, pk=None):
        resource = self.get_object()
        resource.status = Resource.Status.AVAILABLE
        resource.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(resource).data)

    @action(detail=True, methods=["post"])
    def set_unavailable(self, request, pk=None):
        resource = self.get_object()
        resource.status = Resource.Status.UNAVAILABLE
        resource.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(resource).data)


class ResourceSkillViewSet(TenantViewSet):
    queryset = ResourceSkill.objects.select_related("resource")
    serializer_class = ResourceSkillSerializer
    required_permission = "resources.view"
    write_permission = "resources.manage"
    search_fields = ["skill", "resource__name"]
    filterset_fields = ["resource", "level"]


class ResourceAllocationViewSet(TenantViewSet):
    queryset = ResourceAllocation.objects.select_related("resource")
    serializer_class = ResourceAllocationSerializer
    required_permission = "resources.view"
    write_permission = "resources.manage"
    search_fields = ["project_ref", "resource__name"]
    filterset_fields = ["resource", "project_ref", "status"]

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        allocation = self.get_object()
        allocation.status = ResourceAllocation.Status.CONFIRMED
        allocation.save(update_fields=["status", "updated_at"])
        allocation.resource.status = Resource.Status.ALLOCATED
        allocation.resource.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(allocation).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        allocation = self.get_object()
        allocation.status = ResourceAllocation.Status.DONE
        allocation.save(update_fields=["status", "updated_at"])
        resource = allocation.resource
        if not resource.allocations.exclude(status=ResourceAllocation.Status.CONFIRMED).exists():
            resource.status = Resource.Status.AVAILABLE
            resource.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(allocation).data)


class ResourceCalendarViewSet(TenantViewSet):
    queryset = ResourceCalendar.objects.select_related("resource")
    serializer_class = ResourceCalendarSerializer
    required_permission = "resources.view"
    write_permission = "resources.manage"
    search_fields = ["resource__name"]
    filterset_fields = ["resource", "date"]
