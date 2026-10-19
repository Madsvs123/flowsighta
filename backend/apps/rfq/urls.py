from rest_framework.routers import DefaultRouter

from apps.rfq.views import (
    RfqLineViewSet,
    RfqResponseLineViewSet,
    RfqResponseViewSet,
    RfqViewSet,
)

router = DefaultRouter()
router.register("rfq", RfqViewSet, basename="rfqs")
router.register("rfq-lines", RfqLineViewSet, basename="rfq-lines")
router.register("rfq-responses", RfqResponseViewSet, basename="rfq-responses")
router.register("rfq-response-lines", RfqResponseLineViewSet, basename="rfq-response-lines")

urlpatterns = router.urls
