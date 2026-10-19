from rest_framework.routers import DefaultRouter

from apps.manufacturing.views import (
    MaterialIssueViewSet,
    ProductionOrderViewSet,
    ProductionOutputViewSet,
    ProductionStepViewSet,
)

router = DefaultRouter()
router.register("manufacturing/production-orders", ProductionOrderViewSet, basename="production-orders")
router.register("manufacturing/steps", ProductionStepViewSet, basename="production-steps")
router.register("manufacturing/outouts", ProductionOutputViewSet, basename="production-outputs")
router.register("manufacturing/material-issues", MaterialIssueViewSet, basename="material-issues")

urlpatterns = router.urls
