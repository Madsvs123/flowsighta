from rest_framework.routers import DefaultRouter

from apps.yard.views import YardGateLogViewSet, YardLocationViewSet, YardMoveViewSet

router = DefaultRouter()
router.register("yard", YardMoveViewSet, basename="yard")
router.register("yard-locations", YardGateLogViewSet, basename="yard-locations")
router.register("yard-gate-logs", YardGateLogViewSet, basename="yard-gate-logs")

urlpatterns = router.urls
