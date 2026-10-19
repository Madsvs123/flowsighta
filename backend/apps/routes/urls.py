from rest_framework.routers import DefaultRouter

from apps.routes.views import (
    DeliveryStopViewSet,
    DriverAssignmentViewSet,
    RouteStopViewSet,
    RouteViewSet,
)

router = DefaultRouter()
router.register("routes", RouteViewSet, basename="routes")
router.register("route-stops", RouteViewSet, basename="route-stops")
router.register("driver-assignments", DriverAssignmentViewSet, basename="driver-assignments")
router.register("delivery-stops", DeliveryStopViewSet, basename="delivery-stops")

urlpatterns = router.urls
