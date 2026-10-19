from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.compliance.views import (
    ComplianceAssessmentViewSet,
    ComplianceCertificateViewSet,
    ComplianceRequirementViewSet,
    RegulatoryUpdateViewSet,
)

router = DefaultRouter()
router.register("requirements", ComplianceRequirementViewSet, basename="compliancerequirement")
router.register("certificates", ComplianceCertificateViewSet, basename="certificate")
router.register("assessments", ComplianceAssessmentViewSet, basename="complianceassessment")
router.register("regulatory-updates", RegulatoryUpdateViewSet, basename="regulatoryupdate")

urlpatterns = [
    path("compliance/", include(router.urls)),
]
