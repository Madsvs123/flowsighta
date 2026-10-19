from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.supplier_performance.views import (
    PerformanceScorecardViewSet,
    ScorecardMetricViewSet,
)

router = DefaultRouter()
router.register("scorecards", PerformanceScorecardViewSet, basename="performance-scorecard")
router.register("metrics", ScorecardMetricViewSet, basename="scorecard-metric")

urlpatterns = [
    path("supplier_performance/", include(router.urls)),
]
