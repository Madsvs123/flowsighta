from django.db.models import Avg
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.supplier_performance.models import PerformanceScorecard, ScorecardMetric
from apps.supplier_performance.serializers import (
    PerformanceScorecardSerializer,
    ScorecardMetricSerializer,
)


class PerformanceScorecardViewSet(TenantViewSet):
    queryset = PerformanceScorecard.objects.select_related("supplier")
    serializer_class = PerformanceScorecardSerializer
    required_permission = "supplier_performance.view"
    write_permission = "supplier_performance.manage"
    search_fields = ["supplier__name", "supplier__code", "period"]
    filterset_fields = ["supplier", "period", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        metrics = ScorecardMetric.objects.filter(organization=request.organization)
        published = qs.filter(status=PerformanceScorecard.Status.PUBLISHED)
        return Response(
            {
                "scorecard_count": qs.count(),
                "published_scorecards": published.count(),
                "draft_scorecards": qs.filter(status=PerformanceScorecard.Status.DRAFT).count(),
                "archived_scorecards": qs.filter(status=PerformanceScorecard.Status.ARCHIVED).count(),
                "average_composite": float(
                    published.aggregate(v=Avg("composite_score"))["v"] or 0
                ),
                "average_otd": float(
                    published.aggregate(v=Avg("on_time_delivery_rate"))["v"] or 0
                ),
                "average_fill_rate": float(
                    published.aggregate(v=Avg("fill_rate"))["v"] or 0
                ),
                "average_quality_rate": float(
                    published.aggregate(v=Avg("quality_rate"))["v"] or 0
                ),
                "metric_count": metrics.count(),
                "top_scorecards": list(
                    published.order_by("composite_score")[:5].values(
                        "supplier__name", "period", "composite_score"
                    )
                ),
            }
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        scorecard = self.get_object()
        if scorecard.status == PerformanceScorecard.Status.PUBLISHED:
            return Response({"detail": "Scorecard is already published."}, status=400)
        scorecard.composite_score = scorecard.compute_composite()
        scorecard.status = PerformanceScorecard.Status.PUBLISHED
        scorecard.save(update_fields=["composite_score", "status", "updated_at"])
        return Response(self.get_serializer(scorecard).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        scorecard = self.get_object()
        scorecard.status = PerformanceScorecard.Status.ARCHIVED
        scorecard.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(scorecard).data)


class ScorecardMetricViewSet(TenantViewSet):
    queryset = ScorecardMetric.objects.select_related("scorecard", "scorecard__supplier")
    serializer_class = ScorecardMetricSerializer
    required_permission = "supplier_performance.view"
    write_permission = "supplier_performance.manage"
    search_fields = ["scorecard__supplier__name", "scorecard__period"]
    filterset_fields = ["scorecard", "metric"]
