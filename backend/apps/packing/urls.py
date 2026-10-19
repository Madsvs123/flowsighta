from rest_framework.routers import DefaultRouter

from apps.packing.views import BoxViewSet, PackedItemViewSet, PackingSessionViewSet

router = DefaultRouter()
router.register("packing", PackingSessionViewSet, basename="packing")
router.register("packing-boxes", BoxViewSet, basename="packing-boxes")
router.register("packed-items", PackedItemViewSet, basename="packed_item")

urlpatterns = router.urls
