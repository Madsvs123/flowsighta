from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.quality.models import (
    CorrectiveAction,
    InspectionResult,
    NonConformance,
    QualityInspection,
    QualityPlan,
)
from apps.quality.serializers import (
    CorrectiveActionSerializer,
    InspectionResultSerializer,
    NonConformanceSerializer,
    QualityInspectionSerializer,
    QualityPlanSerializer,
)


class QualityPlanViewSet(TenantViewSet):
    queryset = QualityPlan.objects.select_related("product")
    serializer_class = QualityPlanSerializer
    required_permission = "quality.view"
    write_permission = "quality.manage"
    search_fields = ["name", "product__sku", "product__name"]
    filterset_fields = ["status", "product"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = dict(qs.values_list("status").annotate(n=Count("id")))
        nc_qs = NonConformance.objects.filter(organization=request.organization)
        nc_by_status = dict(nc_qs.values_list("status").annotate(n=Count("id")))
        inspections = QualityInspection.objects.filter(organization=request.organization)
        return Response(
            {
                "plans_total": qs.count(),
                "plans_active": by_status.get("draft", 0),
                "inspections_total": inspections.count(),
                "inspections_passed": inspections.filter(status="passed").count(),
                "inspections_failed": inspections.filter(status="failed").count(),
                "nc_total": nc_qs.count(),
                "nc_open": nc_by_status.get("open", 0) + nc_by_status.get("investigating", 0),
                "nc_closed": nc_by_status.get("closed", 0),
                "nc_critical": nc_qs.filter(severity="critical").count(),
                "severity_breakdown": list(
                    nc_qs.values("severity").annotate(count=Count("id")).order_by("severity")
                ),
            }
        )


class QualityInspectionViewSet(TenantViewSet):
    queryset = QualityInspection.objects.select_related("plan", "plan__product", "inspected_by")
    serializer_class = QualityInspectionSerializer
    required_permission = "quality.view"
    write_permission = "quality.manage"
    search_fields = ["reference", "plan__name", "plan__product__sku"]
    filterset_fields = ["plan", "status"]

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        inspection = self.get_object()
        inspection.status = QualityInspection.Status.IN_PROGRESS
        inspection.inspected_by = request.user
        inspection.save(update_fields=["status", "inspected_by", "updated_at"])
        return Response(self.get_serializer(inspection).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        inspection = self.get_object()
        passed = bool(request.data.get("passed", True))
        inspection.status = (
            QualityInspection.Status.PASSED if passed else QualityInspection.Status.FAILED
        )
        inspection.inspected_by = request.user
        inspection.inspected_at = timezone.now()
        inspection.save(update_fields=["status", "inspected_by", "inspected_at", "updated_at"])
        return Response(self.get_serializer(inspection).data)


class InspectionResultViewSet(TenantViewSet):
    queryset = InspectionResult.objects.select_related("inspection")
    serializer_class = InspectionResultSerializer
    required_permission = "quality.view"
    write_permission = "quality.manage"
    search_fields = ["attribute", "inspection__reference"]
    filterset_fields = ["inspection", "pass"]


class NonConformanceViewSet(TenantViewSet):
    queryset = NonConformance.objects.select_related("product").prefetch_related("corrective_actions")
    serializer_class = NonConformanceSerializer
    required_permission = "quality.view"
    write_permission = "quality.manage"
    search_fields = ["reference", "product__sku", "description"]
    filterset_fields = ["status", "severity", "type", "product"]

    @action(detail=True, methods=["post"])
    def investigate(self, request, pk=None):
        nc = self.get_object()
        nc.status = NonConformance.Status.INVESTIGATING
        nc.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(nc).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        nc = self.get_object()
        nc.status = NonConformance.Status.CLOSED
        nc.disposition = request.data.get("disposition", nc.disposition)
        nc.save(update_fields=["status", "disposition", "updated_at"])
        return Response(self.get_serializer(nc).data)


class CorrectiveActionViewSet(TenantViewSet):
    queryset = CorrectiveAction.objects.select_related("nc", "owner")
    serializer_class = CorrectiveActionSerializer
    required_permission = "quality.view"
    write_permission = "quality.manage"
    search_fields = ["action", "nc__reference"]
    filterset_fields = ["nc", "owner", "status"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        ca = self.get_object()
        ca.status = CorrectiveAction.Status.COMPLETED
        ca.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(ca).data)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        ca = self.get_object()
        ca.status = CorrectiveAction.Status.VERIFIED
        ca.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(ca).data)
