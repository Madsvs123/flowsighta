from rest_framework.routers import DefaultRouter

from apps.replenishment.views import (
    ReplenishmentLineViewSet,
    ReplenishmentOrderViewSet,
    ReplenishmentPolicyViewSet,
    ReplenishmentRunViewSet,
)

router = DefaultRouter()
router.register("replenishment/replenishment-policies", ReplenishmentPolicyViewSet, basename="replenishment-policies")
router.register("replenishment/replenishment-runs", ReplenishmentRunViewSet, basename="replenishment-run")
router.register("replenishment/replenishment-lines", ReplenishmentLineViewSet, basename="replenishment-line")
router.register("replenishment/replenishment-orders", ReplenishmentOrderViewSet, basename="replenishment-order")

urlpatterns = router.urls
