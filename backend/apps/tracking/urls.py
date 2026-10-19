from rest_framework.routers import DefaultRouter

from apps.tracking.views import (
    EtaPredictionViewSet,
    GeofenceEventViewSet,
    GeoFenceViewSet,
    TrackingEventViewSet,
)

router = DefaultRouter()
router.register("tracking", TrackingEventViewSet, basename="tracking")
router.register("geofences", GeoFenceViewSet, basename="geofence")
router.register("geofence-events", GeofenceEventViewSet, basename="geofence-events")
router.register("eta-predictions", EtaPredictionViewSet, basename="eta-predictions")

urlpatterns = router.urls
