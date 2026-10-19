from django.db.models import Count, Q
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.audit.models import AuditAction, AuditEngagement, AuditFinding, AuditProgram
from apps.audit.serializers import (
    AuditActionSerializer,
    AuditEngagementSerializer,
    AuditFindingSerializer,
    AuditProgramSerializer,
)
from apps.core.mixins import TenantViewSet


class AuditProgramViewSet(TenantViewSet):
    queryset = AuditProgram.objects.all()
    serializer_class = AuditProgramSerializer
    required_permission = "audit.view"
    write_permission = "audit.manage"
    search_fields = ["name", "period"]
    filterset_fields = ["status", "period"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        programs = self.get_queryset()
        engagements = AuditEngagement.objects.filter(organization=request.organization)
        findings = AuditFinding.objects.filter(organization=request.organization)
        by_severity = {
            s: findings.filter(severity=s).count() for s, _ in AuditFinding.Severity.choices
        }
        open_findings = findings.exclude(status=AuditFinding.Status.CLOSED)
        per_program = list(
            engagements.values("program__name")
            .annotate(total=Count("id"))
            .order_by("-total")[:5]
            .values("program__name", "total")
        )
        return Response(
            {
                "program_count": programs.count(),
                "active_programs": programs.exclude(status=AuditProgram.Status.COMPLETED).count(),
                "engagement_count": engagements.count(),
                "open_findings": open_findings.count(),
                "critical_findings": by_severity.get("critical", 0)
                + by_severity.get("high", 0),
                "by_severity": by_severity,
                "engagements_by_program": per_program,
            }
        )

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        program = self.get_object()
        program.status = AuditProgram.Status.IN_PROGRESS
        program.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(program).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None)
        program = self.get_object()
        program.status = AuditProgram.Status.COMPLETED
        program.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(program).data)


class AuditEngagementViewSet(TenantViewSet):
    queryset = AuditEngagement.objects.select_related("program", "auditor")
    serializer_class = AuditEngagementSerializer
    required_permission = "audit.view"
    write_permission = "audit.manage"
    search_fields = ["scope", "program__name", "auditor__email"]
    filterset_fields = ["program", "auditor", "status"]


class AuditFindingViewSet(TenantViewSet):
    queryset = AuditFinding.objects.select_related("engagement", "engagement__program")
    serializer_class = AuditFindingSerializer
    required_permission = "audit.view"
    write_permission = "audit.manage"
    search_fields = ["description", "engagement__scope", "engagement__program__name"]
    filterset_fields = ["engagement", "severity", "status"]

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        finding = self.get_object()
        finding.status = AuditFinding.Status.ACKNOWLEDGED
        finding.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(finding).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        finding = self.get_object()
        finding.status = AuditFinding.Status.CLOSED
        finding.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(finding).data)


class AuditActionViewSet(TenantViewSet):
    queryset = AuditAction.objects.select_related("finding", "owner")
    serializer_class = AuditActionSerializer
    required_permission = "audit.view"
    write_permission = "audit.manage"
    search_fields = ["action", "finding__description", "owner__email"]
    filterset_fields = ["finding", "owner", "status"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        action_item = self.get_object()
        action_item.status = AuditAction.Status.COMPLETED
        action_item.save(update_fields=["status", "updated_at"])
        finding = action_item.finding
        if (
            finding.status != AuditFinding.Status.ACKNOWLEDGED
            and not finding.actions.exclude(status=AuditAction.Status.COMPLETED).exists()
        ):
            finding.status = AuditFinding.Status.REMEDIATED
            finding.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(action_item).data)
