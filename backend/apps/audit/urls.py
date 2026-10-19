from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.audit.views import (
    AuditActionViewSet,
    AuditEngagementViewSet,
    AuditFindingViewSet,
    AuditProgramViewSet,
)

router = DefaultRouter()
router.register("programs", AuditProgramViewSet, basename="auditprogram")
router.register("engagements", AuditEngagementViewSet, basename="auditengagement")
router.register("findings", AuditFindingViewSet, basename="auditfinding")
router.register("actions", AuditActionViewSet, basename="auditaction")

urlpatterns = [
    path("audits/", include(router.urls)),
]
