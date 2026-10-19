from rest_framework.routers import DefaultRouter

from apps.leave.views import (
    LeaveApprovalViewSet,
    LeaveBalanceViewSet,
    LeavePolicyViewSet,
    LeaveRequestViewSet,
)

router = DefaultRouter()
router.register("leave", LeaveRequestViewSet, basename="leaverequest")
router.register("leave-policy", LeavePolicyViewSet, basename="leavepolicy")
router.register("leave-balances", LeaveBalanceViewSet, basename="leavebalance")
router.register("leave-approvals", LeaveApprovalViewSet, basename="leaveapproval")

urlpatterns = router.urls
