from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.bills_of_materials.models import Bom, BomLine, BomRevision
from apps.bills_of_materials.serializers import BomLineSerializer, BomRevisionSerializer, BomSerializer
from apps.core.mixins import TenantViewSet


class BomViewSet(TenantViewSet):
    queryset = Bom.objects.select_related("product").prefetch_related("lines", "lines__component")
    serializer_class = BomSerializer
    required_permission = "bills_of_materials.view"
    write_permission = "bills_of_materials.manage"
    search_fields = ["product__sku", "product__name", "version"]
    filterset_fields = ["status", "product", "version"]
    ordering_fields = ["created_at", "effective_from"]

    def perform_create(self, serializer):
        instance = serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        BomRevision.objects.create(
            organization=instance.organization,
            bom=instance,
            version=instance.version,
            notes="Initial revision",
            approved_by=self.request.user,
            approved_at=timezone.now(),
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = dict(qs.values_list("status").annotate(n=Count("id")))
        line_count = (
            BomLine.objects.filter(organization=request.organization, bom__in=qs).count()
        )
        return Response(
            {
                "total": qs.count(),
                "draft": by_status.get("draft", 0),
                "active": by_status.get("active", 0),
                "obsolete": by_status.get("obsolete", 0),
                "line_count": line_count,
                "revision_count": BomRevision.objects.filter(organization=request.organization).count(),
                "status_breakdown": [
                    {"status": k, "count": v} for k, v in by_status.items()
                ],
            }
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        bom = self.get_object()
        if bom.status != Bom.Status.DRAFT:
            return Response({"detail": "Only draft BOMs can be activated."}, status=400)
        Bom.objects.filter(organization=bom.organization, product=bom.product, status=Bom.Status.ACTIVE).update(
            status=Bom.Status.OBSOLETE, updated_at=timezone.now()
        )
        bom.status = Bom.Status.ACTIVE
        bom.effective_from = bom.effective_from or timezone.now().date()
        bom.save(update_fields=["status", "effective_from", "updated_at"])
        return Response(self.get_serializer(bom).data)

    @action(detail=True, methods=["post"])
    def obsolete(self, request, pk=None):
        bom = self.get_object()
        bom.status = Bom.Status.DRAFT
        bom.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(bom).data)


class BomLineViewSet(TenantViewSet):
    queryset = BomLine.objects.select_related("bom", "bom__product", "component")
    serializer_class = BomLineSerializer
    required_permission = "bills_of_materials.view"
    write_permission = "bills_of_materials.manage"
    search_fields = ["component__sku", "component__name"]
    filterset_fields = ["bom", "component"]


class BomRevisionViewSet(TenantViewSet):
    queryset = BomRevision.objects.select_related("bom", "bom__product", "approved_by")
    serializer_class = BomRevisionSerializer
    required_permission = "bills_of_materials.view"
    write_permission = "bills_of_materials.manage"
    search_fields = ["version", "notes"]
    filterset_fields = ["bom"]
