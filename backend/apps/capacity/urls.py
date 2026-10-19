from rest_framework.routers import DefaultRouter

from apps.capacity.views import CapacityLoadViewSet, CapacityPlanViewSet, CapacityProfileViewSet

router = DefaultRouter()
router.register("capacity/capacity-profiles", CapacityProfileViewSet, basename="capacity-profile"
router.register("capacity/capacity-loads", CapacityLoadViewSet, basename="capacity-load")
router.register("capacity/capacity-plans", CapacityPlanViewSet, basename="capacity-plan")

urlpatterns = router.urls
