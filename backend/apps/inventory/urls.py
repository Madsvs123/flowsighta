from rest_framework.routers import DefaultRouter

from apps.inventory.views import BatchViewSet, InventoryMovementViewSet, ProductViewSet, SerialNumberViewSet, StockItemViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="products")
router.register("stock", StockItemViewSet, basename="stock")
router.register("batches", BatchViewSet, basename="batches")
router.register("serials", SerialNumberViewSet, basename="serial-number")
router.register("movements", InventoryMovementViewSet, basename="movements")

urlpatterns = router.urls
