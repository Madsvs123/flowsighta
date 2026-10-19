from decimal import Decimal

from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.core.services import next_number
from apps.cycle_counts.models import CountLine, CycleCount
from apps.cycle_counts.serializers import CountLineSerializer, CycleCountSerializer


class CycleCountViewSet(TenantViewSet):
    queryset = CycleCount.objects.select_related("warehouse", "counted_by")
    serializer_class = CycleCountSerializer
    required_permission = "cycle_counts.view"
    write_permission = "cycle_counts.manage"
    search_fields = ["number", "warehouse__code"]
    filterset_fields = ["warehouse", "type", "status"]

    def perform_create(self, serializer):
        instance = serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        if not instance.number:
            instance.number = next_number(CycleCount, instance.organization, "CC")
            instance.save(update_fields=["number"])

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        lines = CountLine.objects.filter(count__organization_id=request.organization.id)
        return Response(
            {
                "count_total": qs.count(),
                "scheduled": qs.filter(status=CycleCount.Status.SCHEDULED).count(),
                "in_progress": qs.filter(status=CycleCount.Status.IN_PROGRESS).count(),
                "completed": qs.filter(status=CycleCount.Status.COMPLETED).count(),
                "approved": qs.filter(status=CycleCount.Status.APPROVED).count(),
                "line_count": lines.count(),
                "lines_matched": lines.filter(status=CountLine.Status.MATCHED).count(),
                "lines_variance": lines.filter(status=CountLine.Status.VARIANCE).count(),
                "total_variance": float(
                    lines.aggregate(total=Sum("variance"))["total"] or 0
                ),
                "by_status": [
                    {"status": s, "count": qs.filter(status=s).count()}
                    for s in CycleCount.Status.values
                ],
            }
        )

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        count = self.get_object()
        if count.status != CycleCount.Status.SCHEDULED:
            return Response({"detail": "Only scheduled counts can be started."}, status=400)
        count.status = CycleCount.Status.IN_PROGRESS
        count.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(count).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        count = self.get_object()
        if count.status not in (
            CycleCount.Status.SCHEDULED,
            CycleCount.Status.IN_PROGRESS,
        ):
            return Response({"detail": "Count cannot be completed in its current state."}, status=400)
        count.status = CycleCount.Status.COMPLETED
        count.save(update_fields=["status", "updated_at"])
        for line in count.lines.select_for_update():
            line.variance = (line.system_qty or 0) - (line.counted_qty or 0)
            line.status = (
                CountLine.Status.MATCHED
                if line.variance == 0
                else CountLine.Status.VARIANCE
            )
            line.save(update_fields=["variance", "status", "updated_at"])
        return Response(self.get_serializer(count).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        count = self.get_object()
        if count.status != CycleCount.Status.COMPLETED:
            return Response({"detail": "Only completed counts can be approved."}, status=400)
        count.status = CycleCount.Status.APPROVED
        count.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(count).data)


class CountLineViewSet(TenantViewSet):
    queryset = CountLine.objects.select_related("count", "product")
    serializer_class = CountLineSerializer
    required_permission = "cycle_counts.view"
    write_permission = "cycle_counts.manage"
    search_fields = ["count__number", "product__sku", "bin"]
    filterset_fields = ["count", "product", "status"]

    @action(detail=True, methods=["post"])
    def record(self, request, pk=None):
        line = self.get_object()
        counted_qty = request.data.get("count_qty")
        if counted_qty is not None:
            line.counted_qty = Decimal(str(counted_qty))
        line.variance = (line.counted_qty or 0) - (line.system_qty or 0)
        line.status = (
            CountLine.Status.MATCHED
            if line.variance == 0
            else CountLine.Status.VARIANCE
        )
        line.save(update_fields=["counted_qty", "variance", "status", "updated_at"])
        return Response(self.get_serializer(line).data)
