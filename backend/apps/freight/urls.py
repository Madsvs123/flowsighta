from rest_framework.routers import DefaultRouter

from apps.freight.views import (
    AccessorialChargeViewSet,
    FreightBillViewSet,
    FreightBookingViewSet,
    FreightQuoteViewSet,
)

router = DefaultRouter()
router.register("freight", FreightQuoteViewSet, basename="freight-quotes")
router.register("freight-bookings", FreightBookingViewSet, basename="freight-bookings")
router.register("freight-bills", FreightBillViewSet, basename="freight-bill")
router.register("freight-accessorials", AccessorialChargeViewSet, basename="freight-accessorials")

urlpatterns = router.urls
