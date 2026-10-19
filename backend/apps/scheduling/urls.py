from rest_framework.routers import DefaultRouter

from apps.scheduling.views import (
    ScheduleConstraintViewSet,
    ScheduleTaskViewSet,
    ScheduleViewSet,
)

router = DefaultRouter()
router.register("scheduling/schedules", ScheduleViewSet, basename="schedule")
router.register("schedule-tasks", ScheduleTaskViewSet, basename="schedule-task")
router.register("scheduling/schedule-constraints", ScheduleConstraintViewSet, basename="schedule-constraint")

urlpatterns = router.urls
