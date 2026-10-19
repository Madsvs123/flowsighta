from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.customs.models import ComplianceRule, CustomsDeclaration, CustomsDocument, HsCode
from apps.customs.serializers import (
    ComplianceRuleSerializer,
    CustomsDeclarationSerializer,
    CustomsDocumentSerializer,
    HsCodeSerializer,
)


class HsCodeViewSet(TenantViewSet):
    queryset = HsCode.objects.all()
    serializer_class = HsCodeSerializer
    required_permission = "customs.view"
    write_permission = "customs.manage"
    search_fields = ["code", "description"]
    filterset_fields = ["is_active"]


class CustomsDeclarationViewSet(TenantViewSet):
    queryset = CustomsDeclaration.objects.select_related("hs_code")
    serializer_class = CustomsDeclarationSerializer
    required_permission = "customs.view"
    write_permission = "customs.manage"
    search_fields = ["number", "shipment_ref", "origin_country", "destination_country"]
    filterset_fields = ["status", "origin_country", "destination_country", "hs_code"]

    @action(detail=False, methods=["get"])
    def summary(self, request)
        qs = self.get_queryset()
        return Response(
            {
                "declaration_count": qs.count(),
                "by_status": {status: qs.filter(status=status).count() for status, _ in CustomsDeclaration.Status.choices},
                "total_declared_value": float(qs.aggregate(v=Sum("declared_value"))["v"] or 0),
                "held_or_rejected": qs.filter(status__in=["held", "rejected"]).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def file(self, request, pk=None):
        declaration = self.get_object()
        if declaration.status == CustomsDeclaration.Status.CLEARED:
            return Response({"detail": "Already cleared."}, status=400)
        declaration.status = CustomsDeclaration.Status.FILED
        declaration.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(declaration).data)

    @action(detail=True, methods=["post"])
    def clear(self, request, pk=None):
        declaration = self.get_object()
        if declaration.status == CustomsDeclaration.Status.REJECTED:
            return Response({"detail": "Rejected declarations cannot be cleared."}, status=400)
        declaration.status = CustomsDeclaration.Status.CLEARED
        declaration.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(declaration).data)

    @action(detail=True, methods=["post"])
    def hold(self, request, pk=None):
        declaration = self.get_object()
        if declaration.status in (CustomsDeclaration.Status.CLEARED, CustomsDeclaration.Status.REJECTED):
            return Response({"detail": "Finalized declarations cannot be held."}, status=400)
        declaration.status = CustomsDeclaration.Status.HELD
        declaration.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(declaration).data)


class CustomsDocumentViewSet(TenantViewSet):
    queryset = CustomsDocument.objects.select_related("declaration")
    serializer_class = CustomsDocumentSerializer
    required_permission = "customs.view"
    write_permission = "customs.manage"
    search_fields = ["type", "title", "declaration__number"]
    filterset_fields = ["declaration", "type", "status"]


class ComplianceRuleViewSet(TenantViewSet):
    queryset = ComplianceRule.objects.all()
    serializer_class = ComplianceRuleSerializer
    required_permission = "customs.view"
    write_permission = "customs.manage"
    search_fields = ["country", "category", "restriction", "description"]
    filterset_fields = ["country", "category"]
