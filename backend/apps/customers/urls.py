from rest_framework.routers import DefaultRouter

from apps.customers.views import (
    CustomerAddressViewSet,
    CustomerAgreementViewSet,
    CustomerContactViewSet,
    CustomerViewSet,
)

router = DefaultRouter()
router.register("customer", CustomerViewSet, basename="customers")
router.register("customer-contacts", CustomerContactViewSet, basename="customer-contacts")
router.register("customer-addresses", CustomerAddressViewSet, basename="customer-addresses")
router.register("customer-agreements", CustomerAgreementViewSet, basename="customer-agreements")

urlpatterns = router.urls
