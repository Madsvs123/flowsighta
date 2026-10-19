from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.compliance.models import (
    ComplianceAssessment,
    ComplianceCertificate,
    ComplianceRequirement,
    RegulatoryUpdate,
)
from apps.compliance.serializers import (
    ComplianceAssessmentSerializer,
    ComplianceCertificateSerializer,
    ComplianceRequirementSerializer,
    RegulatoryUpdateSerializer,
)
from apps.core.mixins import TenantViewSet


class ComplianceRequirementViewSet(TenantViewSet):
    queryset = ComplianceRequirement.objects.all()
    serializer_class = ComplianceRequirementSerializer
    required_permission = "compliance.view"
    write_permission = "compliance.manage"
    search_fields = ["name", "category", "applies_to"]
    filterset_fields = ["category"]


class ComplianceCertificateViewSet(TenantViewSet):
    queryset = ComplianceCertificate.objects.select_related("supplier", "requirement")
    serializer_class = ComplianceCertificateSerializer
    required_permission = "compliance.view"
    write_permission = "compliance.manage"
    search_fields = ["number", "supplier__name", "requirement__name"]
    filterset_fields = ["supplier", "requirement", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        today = timezone.localdate()
        horizon = today + timezone.timedelta(days=30)
        expiring = qs.filter(
            Q(status=ComplianceCertificate.Status.VALID)
            | Q(status=ComplianceCertificate.Status.EXPIRING),
            expires_date__isnull=False,
            expires_date__lte=horizon,
            expires_date__gte=today,
        )
        expired = qs.filter(expires_date__isnull=False, expires_date__lt=today)
        by_status = {
            s: qs.filter(status=s).count() for s, _ in ComplianceCertificate.Status.choices
        }
        by_requirement = list(
            qs.values("requirement__name")
            .annotate(total=Count("id"))
            .order_by("-total")[:5]
            .values("requirement__name", "total")
        )
        return Response(
            {
                "certificate_count": qs.count(),
                "valid": by_status.get("VALID", 0),
                "expiring": expiring.count(),
                "expired": by_status.get("expired", 0) or expired.count(),
                "revoked": by_status.get("revoked", 0),
                "by_requirement": by_requirement,
            }
        )

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        certificate = self.get_object()
        certificate.status = ComplianceCertificate.Status.REVOKED
        certificate.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(certificate).data)

    @action(detail=True, methods=["post"])
    def mark_expiring(self, request, pk=None):
        certificate = self.get_object()
        certificate.status = ComplianceCertificate.Status.EXPIRING
        certificate.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(certificate).data)


class ComplianceAssessmentViewSet(TenantViewSet):
    queryset = ComplianceAssessment.objects.select_related("certificate", "assessor")
    serializer_class = ComplianceAssessmentSerializer
    required_permission = "compliance.view"
    write_permission = "compliance.manage"
    search_fields = ["certificate__number", "notes", "assessor__email"]
    filterset_fields = ["certificate", "result", "assessor"]


class RegulatoryUpdateViewSet(TenantViewSet):
    queryset = RegulatoryUpdate.objects.all()
    serializer_class = RegulatoryUpdateSerializer
    required_permission = "compliance.view"
    write_permission = "compliance.manage"
    search_fields = ["title", "region", "summary"]
    filterset_fields = ["region", "status"]

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        update = self.get_object()
        update.status = RegulatoryUpdate.Status.PUBLISHED
        update.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(update).data)
