from rest_framework.routers import DefaultRouter

from apps.planning.views import (
    DemandForecastViewSet,
    HistoricalDemandViewSet,
    InventoryProjectionViewSet,
    PlanningConfigViewSet,
    PurchaseRequirementViewSet,
    ReplenishmentRecommendationViewSet,
)

router = DefaultRouter()
router.register("planning-config", PlanningConfigViewSet, basename="planning-config")
router.register("forecasts", DemandForecastViewSet, basename="forecasts")
router.register("historical-demand", HistoricalDemandViewSet, basename="historical-demand")
router.register("projections", InventoryProjectionViewSet, basename="projections")
router.register("replenishments", ReplenishmentRecommendationViewSet, basename="replenishment")
router.register("purchase-requirement", PurchaseRequirementViewSet, basename="purchase-requirements")

urlpatterns = router.urls
