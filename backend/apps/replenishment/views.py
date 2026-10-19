from django.db.models import Avg, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.replenishment.models import (
    ReplenishmentLine,
    ReplenishmentOrder,
    ReplenishmentPolicy,
    ReplenishmentRun,
)
from apps.replenishment.serializers import (
    ReplenishmentLineSerializer,
    ReplenishmentOrderSerializer,
    ReplenishmentPolicySerializer,
    ReplenishmentRunSerializer,
)
from apps.replenishment.tasks import run_replenishment_planning


class ReplenishmentPolicyViewSet(TenantViewSet):
    queryset = ReplenishmentPolicy.objects.select_related("product", "warehouse")
    serializer_class = ReplenishmentPolicySerializer
    required_permission = "replenishment.view"
    write_permission = "replenishment.manage"
    search_fields = ["product__sku", "product__name", "warehouse__name"]
    filterset_fields = ["product", "warehouse", "method", "is_active"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        lines = ReplenishmentLine.objects.filter(organization=request.organization)
        return Response(
            {
                "total": qs.count(),
                "active": qs.filter(is_active=True).count(),
                "warehouses_covered": qs.values("warehouse").distinct().count(),
                "products_covered": qs.values("product").distinct().count(),
                "avg_min_stock": float(qs.aggregate(a=Avg("min_stock"))["a"] or 0),
                "avg_max_stock": float(qs.aggregate(a=Avg("max_stock"))["a"] or 0),
                "proposed_lines": lines.filter(status=ReplenishmentLine.Status.APPROVED).count(),
                "approved_lines": lines.filter(status=ReplenishmentLine.Status.APPROVED).count(),
                "suggested_qty_total": float(
                    lines.aggregate(s=Sum("suggested_qty"))["s"] or 0
                ),
            }
        )


class ReplenishmentRunViewSet(TenantViewSet):
    queryset = ReplenishmentRun.objects.prefetch_related("lines")
    serializer_class = ReplenishmentRunSerializer
    required_permission = "replenishment.view"
    write_permission = "replenishment.manage"
    search_fields = ["number"]
    filterset_fields = ["status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        return Response(
            {
                "total": qs.count(),
                "queued": qs.filter(status=ReplenishmentRun.Status.QUEUED).count(),
                "running": qs.filter(status=ReplenishmentRun.Status.RUNNING).count(),
                "completed": qs.filter(status=ReplenishmentRun.Status.COMPLETED).count(),
                "line_count": ReplenishmentLine.objects.filter(
                    organization=request.organization
                ).count(),
                "order_count": ReplenishmentOrder.objects.filter(
                    organization=request.organization
                ).count(),
            }
        )

    @action(detail=False, methods=["post"])
    def run_planning(self, request):
        result = run_replenishment_planning(organization_id=request.organization.id)
        return Response(result)

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        run = self.get_object()
        if run.status == ReplenishmentRun.Status.COMPLETED:
            return Response({"detail": "Completed runs cannot be re-run."}, status=400)
        run.status = ReplenishmentRun.Status.RUNNING
        run.started_at = timezone.now()
        run.save(update_fields=["status", "started_at", "updated_at"])
        run.status = ReplenishmentRun.Status.COMPLETED
        run.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(run).data)


class ReplenishmentLineViewSet(TenantViewSet):
    queryset = ReplenishmentLine.objects.select_related("run", "product", "warehouse")
    serializer_class = ReplenishmentLineSerializer
    required_permission = "replenishment.view"
    write_permission = "replenishment.manage"
    search_fields = ["product__sku", "run__number"]
    filterset_fields = ["run", "product", "warehouse", "source", "status"]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        line = self.get_object()
        line.status = ReplenishmentLine.Status.APPROVED
        line.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(line).data)

    @action(detail=True, methods=["post"])
    def skip(self, request, pk=None):
        line = self.get_object()
        line.status = ReplenishmentLine.Status.SKIPPED
        line.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(line).data)


class ReplenishmentOrderViewSet(TenantViewSet):
    queryset = ReplenishmentOrder.objects.select_related("run", "supplier")
    serializer_class = ReplenishmentOrderSerializer
    required_permission = "replenishment.view"
    write_permission = "replenishment.manage"
    search_fields = ["run__number", "supplier__name"]
    filterset_fields = ["run", "supplier", "status"]

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        order = self.get_object()
        if order.status == ReplenishmentOrder.Status.CANCELLED:
            order.status = ReplenishmentOrder.Status.ISSUED
            order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        order.status = ReplenishmentOrder.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)
