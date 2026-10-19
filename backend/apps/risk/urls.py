from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.risk.views import (
    RiskAssessmentViewSet,
    RiskMitigationViewSet,
    RiskRegisterViewSet,
    RiskReviewViewSet,
)

router = DefaultRouter()
router.register("register", RiskRegisterViewSet, basename="riskregister")
router.register("assessments", RiskAssessmentViewSet, basename="riskassessment")
router.register("mitigations", RiskMitigationViewSet, basename="riskmitigation")
router.register("reviews", RiskReviewViewSet, basename="riskreview")

urlpatterns = [
    path("risks/", include(router.urls)),
]
