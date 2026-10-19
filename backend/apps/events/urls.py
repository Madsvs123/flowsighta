from rest_framework.routers import DefaultRouter

from apps.events.views import AlertRuleViewSet, ResolutionActionViewSet, SupplyChainEventViewSet

router = DefaultRouter()
router.register("supply-event", SupplyChainEventViewSet, basename="alerts")
router.register("alert-rules", AlertRuleViewSet, basename="alert-rules")
router.register("resolution-actions", ResolutionActionViewSet, basename="resolution-actions")

urlpatterns = router.urls
