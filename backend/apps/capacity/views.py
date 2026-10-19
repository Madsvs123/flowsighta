from django.db.models import Avg, Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.capacity.models import CapacityLoad, CapacityPlan, CapacityProfile
from apps.capacity.serializers import (
    CapacityLoadSerializer,
    CapacityPlanSerializer,
    CapacityProfileSerializer,
)
from apps.capacity.tasks import compute_capacity_loads
from apps.core.mixins import TenantViewSet


class CapacityProfileViewSet(TenantViewSet):
    queryset = CapacityProfile.objects.all()
    serializer_class = CapacityProfileSerializer
    required_permission = "capacity.view"
    write_permission = "capacity.manage"
    search_fields = ["name", "workcenter"]
    filterset_fields = ["is_active"]

    @action(detail=False, methods=["post"])
    def recompute(self, request):
        result = compute_capacity_loads(organization_id=request.organization.id)
        return Response(result)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        loads = CapacityLoad.objects.filter(organization=request.organization)
        plans = CapacityPlan.objects.filter(organization=request.organization)
        return Response(
            {
                "total": qs.count(),
                "active": qs.filter(is_active=True).count(),
                "avg_available_hours": float(
                    qs.aggregate(a=Avg("available_hours"))["a"] or 0
                ),
                "avg_efficiency_pct": float(
                    qs.aggregate(a=Avg("efficiency_pct"))["a"] or 0
                ),
                "load_count": loads.count(),
                "load_hours_total": float(loads.aggregate(s=Sum("load_hours"))["s"] or 0),
                "plan_count": plans.count(),
                "published_plans": plans.filter(status=CapacityPlan.Status.DRAFT).count(),
                "avg_utilization_pct": float(
                    plans.aggregate(a=Avg("utilization_pct"))["a"] or 0
                ),
            }
        )


class CapacityLoadViewSet(TenantViewSet):
    queryset = CapacityLoad.objects.select_related("profile")
    serializer_class = CapacityLoadSerializer
    required_permission = "capacity.view"
    write_permission = "capacity.manage"
    search_fields = ["profile__name"]
    filterset_fields = ["profile", "date"]


class CapacityPlanViewSet(TenantViewSet):
    queryset = CapacityPlan.objects.select_related("profile")
    serializer_class = CapacityPlanSerializer
    required_permission = "capacity.view"
    write_permission = "capacity.manage"
    search_fields = ["profile__name"]
    filterset_fields = ["profile", "status"]

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        plan = self.get_object()
        plan.status = CapacityPlan.Status.PUBLISHED
        plan.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(plan).data)

    @action(detail=True, methods=["post"])
    def refresh_utilization(self, request, pk=None):
        plan = self.get_object()
        if plan.planned_hours:
            plan.utilization_pct = min(
                float(plan.actual_hours) / float(plan.planned_hours) * 100, 100
            )
            plan.save(update_fields=["utilization_pct", "updated_at"])
        return Response(self.get_serializer(plan).data)
