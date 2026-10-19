from rest_framework.routers import DefaultRouter

from apps.logistics.views import (
    CarrierServiceLevelViewSet,
    CarrierViewSet,
    ConsolidationViewSet,
    ContainerViewSet,
    DeliveryScheduleViewSet,
    FreightCostViewSet,
    LogisticsExceptionViewSet,
    PackageViewSet,
    ProofOfDeliveryViewSet,
    RouteViewSet,
    ShipmentMilestoneViewSet,
    ShipmentViewSet,
    TrackingEventViewSet,
)

router = DefaultRouter()
router.register("carriers", CarrierViewSet, basename="carriers")
router.register("carrier-services", CarrierServiceLevelViewSet, basename="carrier-services")
router.register("routes", RouteViewSet, basename="routes")
router.register("shipments", ShipmentViewSet, basename="shipments"
router.register("containers", ContainerViewSet, basename="containers")
router.register("packages", PackageViewSet, basename="packages")
router.register("milestones", ShipmentMilestoneViewSet, basename="milestones")
router.register("tracking-event", TrackingEventViewSet, basename="tracking-events")
router.register("proof-of-delivery", ProofOfDeliveryViewSet, basename="proof-of-delivery")
router.register("freight-costs", FreightCostViewSet, basename="freight-costs")
router.register("consolidations", ConsolidationViewSet, basename="consolidations")
router.register("delivery-schedules", DeliveryScheduleViewSet, basename="delivery-schedules")
router.register("logistics-exceptions", LogisticsExceptionViewSet, basename="logistics-exceptions")

urlpatterns = router.urls
