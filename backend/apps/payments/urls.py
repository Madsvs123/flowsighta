from rest_framework.routers import DefaultRouter

from apps.payments.views import (
    PaymentAllocationViewSet,
    PaymentRunViewSet,
    PaymentTermViewSet,
    PaymentViewSet,
)

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payments")
router.register("payment-terms", PaymentTermViewSet, basename="payment-terms")
router.register("payment-runs", PaymentRunViewSet, basename="payment-runs")
router.register("payment-allocations", PaymentAllocationViewSet, basename="payment_allocation")

urlpatterns = router.urls
