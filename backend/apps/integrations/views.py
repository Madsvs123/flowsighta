from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.integrations.models import (
    Integration,
    IntegrationConnection,
    IntegrationLog,
    WebhookEndpoint,
)
from apps.integrations.serializers import (
    IntegrationConnectionSerializer,
    IntegrationLogSerializer,
    IntegrationSerializer,
    WebhookEndpointSerializer,
)


class IntegrationViewSet(TenantViewSet):
    queryset = Integration.objects.select_related("created_by").annotate(
        connection_count=Count("connections", distinct=True)
    )
    serializer_class = IntegrationSerializer
    required_permission = "integrations.view"
    write_permission = "integrations.manage"
    search_fields = ["name", "provider"]
    filterset_fields = ["provider", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        integrations = self.get_queryset()
        connections = IntegrationConnection.objects.filter(organization=request.organization)
        logs = IntegrationLog.objects.filter(organization=request.organization)
        webhooks = WebhookEndpoint.objects.filter(organization=request.organization)
        return Response(
            {
                "integration_count": integrations.count(),
                "connected_integrations": integrations.filter(status=Integration.Status.CONNECTED).count(),
                "error_integrations": integrations.filter(status=Integration.Status.ERROR).count(),
                "disabled_integrations": integrations.filter(status=Integration.Status.DISABLED).count(),
                "connection_count": connections.count(),
                "connected_connections": connections.filter(
                    status=IntegrationConnection.Status.CONNECTED
                ).count(),
                "disconnected_connections": connections.filter(
                    status=IntegrationConnection.Status.DISCONNECTED
                ).count(),
                "error_connections": connections.filter(status=IntegrationConnection.Status.ERROR).count(),
                "webhook_count": webhooks.count(),
                "active_webhooks": webhooks.filter(status=WebhookEndpoint.Status.ACTIVE).count(),
                "log_count": logs.count(),
                "error_logs": logs.filter(status=IntegrationLog.Status.ERROR).count(),
                "integrations_by_status": {
                    s: integrations.filter(status=s).count() for s, _ in Integration.Status.choices
                },
            }
        )

    @action(detail=True, methods=["post"])
    def connect(self, request, pk=None):
        integration = self.get_object()
        integration.status = Integration.Status.CONNECTED
        integration.save(update_fields=["status", "updated_at"])
        connection, _ = IntegrationConnection.objects.get_or_create(
            organization=integration.organization,
            integration=integration,
            name=f"{integration.provider} default",
            defaults={"status": IntegrationConnection.Status.CONNECTED, "last_checked_at": timezone.now()},
        )
        return Response(self.get_serializer(integration).data)

    @action(detail=True, methods=["post"])
    def disable(self, request, pk=None):
        integration = self.get_object()
        integration.status = Integration.Status.DISABLED
        integration.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(integration).data)


class IntegrationConnectionViewSet(TenantViewSet):
    queryset = IntegrationConnection.objects.select_related("integration").annotate(
        log_count=Count("logs", distinct=True)
    )
    serializer_class = IntegrationConnectionSerializer
    required_permission = "integrations.view"
    write_permission = "integrations.manage"
    search_fields = ["name", "integration__name", "integration__provider"]
    filterset_fields = ["integration", "status"]

    @action(detail=True, methods=["post"])
    def check(self, request, pk=None):
        connection = self.get_object()
        connection.last_checked_at = timezone.now()
        if connection.status != IntegrationConnection.Status.ERROR:
            connection.status = IntegrationConnection.Status.CONNECTED
        connection.save(update_fields=["status", "last_checked_at", "updated_at"])
        IntegrationLog.objects.create(
            organization=connection.organization,
            connection=connection,
            direction=IntegrationLog.Direction.IN,
            status=IntegrationLog.Status.SUCCESS,
            payload_ref=f"health/{connection.pk}",
        )
        return Response(self.get_serializer(connection).data)


class IntegrationLogViewSet(TenantViewSet):
    queryset = IntegrationLog.objects.select_related("connection", "connection__integration")
    serializer_class = IntegrationLogSerializer
    required_permission = "integrations.view"
    write_permission = "integrations.manage"
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["payload_ref", "connection__name", "connection__integration__name"]
    filterset_fields = ["connection", "direction", "status"]


class WebhookEndpointViewSet(TenantViewSet):
    queryset = WebhookEndpoint.objects.select_related("created_by")
    serializer_class = WebhookEndpointSerializer
    required_permission = "integrations.view"
    write_permission = "integrations.manage"
    search_fields = ["name", "url"]
    filterset_fields = ["status"]

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        endpoint = self.get_object()
        endpoint.status = WebhookEndpoint.Status.PAUSED
        endpoint.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(endpoint).data)

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        endpoint = self.get_object()
        endpoint.status = WebhookEndpoint.Status.ACTIVE
        endpoint.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(endpoint).data)
