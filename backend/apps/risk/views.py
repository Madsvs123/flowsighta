from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.risk.models import RiskAssessment, RiskMitigation, RiskRegister, RiskReview
from apps.risk.serializers import (
    RiskAssessmentSerializer,
    RiskMitigationSerializer,
    RiskRegisterSerializer,
    RiskReviewSerializer,
)

IMPACT_WEIGHTS = {"low": 1, "medium": 2, "high": 3, "critical": 4}
LIKELIHOOD_WEIGHTS = {"low": 1, "medium": 2, "high": 3}


def compute_score(impact, likelihood):
    return IMPACT_WEIGHTS.get(impact, 1) * LIKELIHOOD_WEIGHTS.get(likelihood, 1


class RiskRegisterViewSet(TenantViewSet):
    queryset = RiskRegister.objects.select_related("owner")
    serializer_class = RiskRegisterSerializer
    required_permission = "risk.view"
    write_permission = "risk.manage"
    search_fields = ["name", "category", "description", "owner__email"]
    filterset_fields = ["category", "impact", "likelihood", "status", "owner"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = {s: qs.filter(status=s).count() for s, _ in RiskRegister.Status.choices}
        by_impact = {s: qs.filter(impact=s).count() for s, _ in RiskRegister.Impact.choices}
        open_risks = qs.exclude(status=RiskRegister.Status.ACCEPTED)
        top = list(
            open_risks.order_by("-score")[:5].values("name", "impact", "likelihood", "score", "status")
        )
        return Response(
            {
                "risk_count": qs.count(),
                "open": by_status.get("identified", 0) + by_status.get("assessed", 0),
                "mitigated": by_status.get("mitigated", 0),
                "accepted": by_status.get("accepted", 0),
                "by_impact": by_impact,
                "avg_score": round(sum(r.score or 0 for r in open_risks) / max(open_risks.count(), 1), 1),
                "top_risks": top,
            }
        )

    @action(detail=True, methods=["post"])
    def assess(self, request, pk=None):
        risk = self.get_object()
        impact = request.data.get("impact", risk.impact)
        likelihood = request.data.get("likelihood", risk.likelihood)
        score = compute_score(impact, likelihood)
        RiskAssessment.objects.create(
            organization=risk.organization,
            risk=risk,
            date=request.data.get("date") or timezone.localdate(),
            assessor=request.user,
            impact=impact,
            likelihood=likelihood,
            score=score,
        )
        risk.impact = impact
        risk.likelihood = likelihood
        risk.score = score
        risk.status = RiskRegister.Status.ASSESSED
        risk.save(update_fields=["impact", "likelihood", "score", "status", "updated_at"])
        return Response(self.get_serializer(risk).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        risk = self.get_object()
        risk.status = RiskRegister.Status.ACCEPTED
        risk.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(risk).data)


class RiskAssessmentViewSet(TenantViewSet):
    queryset = RiskAssessment.objects.select_related("risk", "assessor")
    serializer_class = RiskAssessmentSerializer
    required_permission = "risk.view"
    write_permission = "risk.manage"
    search_fields = ["risk__name", "assessor__email"]
    filterset_fields = ["risk", "assessor", "impact", "likelihood"]


class RiskMitigationViewSet(TenantViewSet):
    queryset = RiskMitigation.objects.select_related("risk", "owner")
    serializer_class = RiskMitigationSerializer
    required_permission = "risk.view"
    write_permission = "risk.manage"
    search_fields = ["action", "risk__name", "owner__email"]
    filterset_fields = ["risk", "owner", "status"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        mitigation = self.get_object()
        mitigation.status = RiskMitigation.Status.COMPLETED
        mitigation.save(update_fields=["status", "updated_at"])
        risk = mitigation.risk
        if (
            risk.status == RiskRegister.Status.ACCEPTED
            and not risk.mitigations.exclude(status=RiskMitigation.Status.COMPLETED).exists()
        ):
            risk.status = RiskRegister.Status.MITIGATED
            risk.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(mitigation).data)


class RiskReviewViewSet(TenantViewSet):
    queryset = RiskReview.objects.select_related("risk", "reviewed_by")
    serializer_class = RiskReviewSerializer
    required_permission = "risk.view"
    write_permission = "risk.manage"
    search_fields = ["risk__name", "notes", "reviewed_by__email"]
    filterset_fields = ["risk", "reviewed_by"]
