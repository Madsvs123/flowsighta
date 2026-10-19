from django.utils import timezone
from django.db.models import Avg, Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.mrp.models import MrpException, MrpRequirement, MrpRun
from apps.mrp.serializers import MrpExceptionSerializer, MrpRequirementSerializer, MrpRunSerializer
from apps.mrp.tasks import run_mrp_for_organizations


class MrpRunViewSet(TenantViewSet):
    queryset = MrpRun.objects.all()
    serializer_class = MrpRunSerializer
    required_permission = "mrp.view"
    write_permission = "mrp.manage"
    search_fields = ["number"]
    filterset_fields = ["status"]

    @action(detail=False, methods=["get"])
    def summary(self, request)
        qs = self.get_queryset()
        requirements = MrpRequirement.objects.filter(organization=request.organization)
        exceptions = MrpException.objects.filter(organization=request.organization)
        return Response(
            {
                "total": qs.count(),
                "queued": qs.filter(status=MrpRun.Status.QUEUED).count(),
                "running": qs.filter(status=MrpRun.Status.RUNNING).count(),
                "completed": qs.filter(status=MrpRun.Status.COMPLETED).count(),
                "failed": qs.filter(status=MrpRun.Status.FAILED).count(),
                "requirement_count": requirements.count(),
                "net_requirement_total": float(
                    requirements.aggregate(s=Sum("net_requirement"))["s"] or 0
                ),
                "planned_order_value": float(
                    requirements.aggregate(s=Sum("planned_order_qty"))["s"] or 0
                ),
                "exception_count": exceptions.count(),
                "shortage_count": exceptions.filter(type=MrpException.Type.SHORTAGE).count(),
            }
        )

    @action(detail=False, methods=["post"])
    def run_all(self, request):
        result = run_mrp_for_organizations(organization_id=request.organization.id)
        return Response(result)

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        run = self.get_object()
        if run.status not in (MrpRun.Status.QUEUED, MrpRun.Status.FAILED):
            return Response({"detail": "Only queued or failed runs can be (re)started."}, status=200)
        run.status = MrpRun.Status.RUNNING
        run.started_at = timezone.now()
        run.save(update_fields=["status", "started_at", "updated_at"])
        run.status = MrpRun.Status.COMPLETED
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "finished_at", "updated_at"])
        return Response(self.get_serializer(run).data)


class MrpRequirementViewSet(TenantViewSet):
    queryset = MrpRequirement.objects.select_related("run", "product")
    serializer_class = MrpRequirementSerializer
    required_permission = "mrp.view"
    write_permission = "mrp.manage"
    search_fields = ["product__sku", "product__name", "run__number"]
    filterset_fields = ["run", "product"]


class MrpExceptionViewSet(TenantViewSet):
    queryset = MrpException.objects.select_related("run", "product")
    serializer_class = MrpExceptionSerializer
    required_permission = "mrp.view"
    write_permission = "mrp.manage"
    search_fields = ["product__sku", "message"]
    filterset_fields = ["run", "product", "type"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        return Response(
            {
                "total": qs.count(),
                "by_type": {t: qs.filter(type=t).count() for t, _ in MrpException.Type.choices},
                "open_shortages": qs.filter(type=MrpException.Type.SHORTAGE).count(),
            }
        )
