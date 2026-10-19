from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.integrations.models import (
    Integration,
    IntegrationConnection,
    IntegrationLog,
    WebhookEndpoint,
)


class IntegrationSerializer(TenantSerializer):
    connection_count = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source="created_by.first_name", read_only=True)

    class Meta:
        model = Integration
        fields = (
            "id",
            "name",
            "provider",
            "config",
            "status",
            "connection_count",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "status")


class IntegrationConnectionSerializer(TenantSerializer):
    integration_name = serializers.CharField(source="integration.name", read_only=True)
    integration_provider = serializers.CharField(source="integration.provider", read_only=True)
    log_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = IntegrationConnection
        fields = (
            "id",
            "integration",
            "integration_name",
            "integration_provider",
            "name",
            "status",
            "log_count",
            "last_checked_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "last_checked_at", "created_at", "updated_at")


class IntegrationLogSerializer(TenantSerializer):
    connection_name = serializers.CharField(source="connection.name", read_only=True)
    integration_name = serializers.CharField(source="connection.integration.name", read_only=True)

    class Meta:
        model = IntegrationLog
        fields = (
            "id",
            "connection",
            "connection_name",
            "integration_name",
            "direction",
            "status",
            "payload_ref",
            "occurred_at",
        )
        read_only_fields = ("id", "occurred_at")


class WebhookEndpointSerializer(TenantSerializer):
    created_by_name = serializers.CharField(source="created_by.first_name", read_only=True)

    class Meta:
        model = WebhookEndpoint
        fields = (
            "id",
            "name",
            "url",
            "events",
            "secret",
            "status",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "secret", "created_at", "updated_at")
