from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.transfers.views import TransferLineViewSet, TransferOrderViewSet, TransferShipmentViewSet

router = DefaultRouter()
router.register("transfer-orders", TransferOrderViewSet, basename="transfer-order")
router.register("transfer-lines", TransferLineViewSet, basename="transferlines")
router.register("transfer-shipments", TransferShipmentViewSet, basename="transfershipments")

urlpatterns = [
    path("transfers/", include(router.urls)),
]
