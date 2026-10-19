from rest_framework.routers import DefaultRouter

from apps.attendance.views import (
    AttendanceRecordViewSet,
    OvertimeRequestViewSet,
    ShiftAssignmentViewSet,
    ShiftViewSet,
)

router = DefaultRouter()
router.register("attendance", AttendanceRecordViewSet, basename="attendance")
router.register("shifts", ShiftViewSet, basename="shift")
router.register("shift-assignments", ShiftAssignmentViewSet, basename="shiftassignment")
router.register("overtime-requests", OvertimeRequestViewSet, basename="overtimerequest")

urlpatterns = router.urls
