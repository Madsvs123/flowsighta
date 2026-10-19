from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.receiving.views import PutawayTaskViewSet, ReceiptLineViewSet, ReceiptViewSet

router = DefaultRouter()
router.register("receipts", ReceiptViewSet, basename="receipt")
router.register("receipt-lines", ReceiptLineViewSet, basename="receiptlines")
router.register("putaway-tasks", PutawayTaskViewSet, basename="putawaytasks")

urlpatterns = [
    path("receiving/", include(router.urls)),
]
