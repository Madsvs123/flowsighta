from rest_framework.routers import DefaultRouter

from apps.costing.views import (
    CostingMethodViewSet,
    CostLayerViewSet,
    CostVarianceViewSet,
    InventoryValuationViewSet,
)

router = DefaultRouter()
router.register("methods", CostingMethodViewSet, basename="methods"
router.register("cost-layers", CostLayerViewSet, basename="cost-layers")
router.register("variances", CostVarianceViewSet, basename="variances")
router.register("valuations", InventoryValuationViewSet, basename="valuations")

urlpatterns = router.urls
