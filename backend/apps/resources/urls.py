from rest_framework.routers import DefaultRouter

from apps.resources.views import (
    ResourceAllocationViewSet,
    ResourceCalendarViewSet,
    ResourceSkillViewSet,
    ResourceViewSet,
)

router = DefaultRouter()
router.register("resources", ResourceViewSet, basename="resource")
router.register("resource-skills", ResourceSkillViewSet, basename="resourceskill")
router.register("resource-allocations", ResourceAllocationViewSet, basename="resourceallocation")
router.register("resource-calendars", ResourceCalendarViewSet, basename="resourcecalendar")

urlpatterns = router.urls
