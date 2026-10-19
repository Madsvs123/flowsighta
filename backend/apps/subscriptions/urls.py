from rest_framework.routers import DefaultRouter

from apps.subscriptions.views import (
    RenewalViewSet,
    SubscriptionInvoiceViewSet,
    SubscriptionLineViewSet,
    SubscriptionViewSet,
)

router = DefaultRouter()
router.register("subscriptions", SubscriptionViewSet, basename="subscriptions")
router.register("subscription-lines", SubscriptionLineViewSet, basename="subscription-lines")
router.register("subscription-invoices", SubscriptionInvoiceViewSet, basename="subscription-invoices")
router.register("renewals", SubscriptionInvoiceViewSet, basename="renewals")

urlpatterns = router.urls
