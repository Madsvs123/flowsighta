from rest_framework.routers import DefaultRouter

from apps.integrations.views import (
    IntegrationConnectionViewSet,
    IntegrationLogViewSet,
    IntegrationViewSet,
    WebhookEndpointViewSet,
)

router = DefaultRouter()
router.register("integrations", IntegrationViewSet, basename="integration")
router.register("integration-connections", IntegrationConnectionViewSet, basename="integrationconnection")
router.register("integration-log", IntegrationLogViewSet, basename="integrationlog")
router.register("webhook-endpoints", WebhookEndpointViewSet, basename="webhookendpoint")

urlpatterns = router.urls
