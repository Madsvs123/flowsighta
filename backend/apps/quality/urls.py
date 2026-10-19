from rest_framework.routers import DefaultRouter

from apps.quality.views import (
    CorrectiveActionViewSet,
    InspectionResultViewSet,
    NonConformanceViewSet,
    QualityInspectionViewSet,
    QualityPlanViewSet,
)

router = DefaultRouter()
router.register("quality/plans", QualityPlanViewSet, basename="quality-plans")
router.register("quality/inspections", QualityInspectionViewSet, basename="quality-inspections")
router.register("quality/results", InspectionResultViewSet, basename="quality-results")
router.register("quality/non-conformances", NonConformanceViewSet, basename="quality-non-conformances")
router.register("quality/corrective-actions", CorrectiveActionViewSet, basename="corrective-actions")

urlpatterns = router.urls
