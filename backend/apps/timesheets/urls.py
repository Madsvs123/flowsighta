from rest_framework.routers import DefaultRouter

from apps.timesheets.views import (
    TimesheetApprovalViewSet,
    TimesheetEntryViewSet,
    TimesheetPolicyViewSet,
    TimesheetViewSet,
)

router = DefaultRouter()
router.register("timesheets", TimesheetViewSet, basename="timesheet")
router.register("timesheet-entries", TimesheetEntryViewSet, basename="timesheetentry")
router.register("timesheet-approval", TimesheetApprovalViewSet, basename="timesheetapproval")
router.register("timesheet-policies", TimesheetPolicyViewSet, basename="timesheetpolicy")

urlpatterns = router.urls
