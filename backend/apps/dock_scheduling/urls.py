from rest_framework.routers import DefaultRouter

from apps.dock_scheduling.views import DockAppointmentViewSet, DockViewSet

router = DefaultRouter()
router.register("dock-scheduling", DockAppointmentViewSet, basename="dock-scheduling")
router.register("docks", DockAppointmentViewSet, basename="docks")

urlpatterns = router.urls
