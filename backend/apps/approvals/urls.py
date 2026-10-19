from rest_framework.routers import DefaultRouter

from apps.approvals.views import (
    ApprovalDecisionViewSet,
    ApprovalPolicyViewSet,
    ApprovalRequestViewSet,
    ApprovalStepViewSet,
)

router = DefaultRouter()
router.register("approval-policies", ApprovalPolicyViewSet, basename="approval-policies")
router.register("approval-request", ApprovalRequestViewSet, basename="approval-requests")
router.register("approval-steps", ApprovalStepViewSet, basename="approval-steps")
router.register("approval-decisions", ApprovalDecisionViewSet, basename="approval-decisions")

urlpatterns = router.urls
