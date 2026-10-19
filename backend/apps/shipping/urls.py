from rest_framework.routers import DefaultRouter

from apps.shipping.views import OutboundLineViewSet, OutboundOrderViewSet, ShipmentPlanViewSet

router = DefaultRouter()
router.register("shipping", OutboundOrderViewSet, basename="shipping")
router.register("outbound-lines", OutboundLineViewSet, basename="outbound-lines")
router.register("shipment-plans", OutboundOrderViewSet, basename="shipment-plans")

urlpatterns = router.urls
