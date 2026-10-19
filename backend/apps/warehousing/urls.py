from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.warehousing.views import BinViewSet, PutawayRuleViewSet, StorageZoneViewSet

router = DefaultRouter()
router.register("storage-zones", StorageZoneViewSet basename="storagezones")
router.register("bins", BinViewSet, basename="bin")
router.register("putaway-rules", PutawayRuleViewSet, basename="putawayrules")

urlpatterns = [
    path("warehousing/", include(router.urls)),
]
