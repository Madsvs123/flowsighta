from django.contrib import admin

from apps.integrations.models import (
    Integration,
    IntegrationConnection,
    IntegrationLog,
    WebhookEndpoint,
)


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "status", "created_at")
    list_filter = ("provider", "status")
    search_fields = ("name", "provider")


@admin.register(IntegrationConnection)
class IntegrationConnectionAdmin(admin.ModelAdmin):
    list_display = ("integration", "name", "status", "last_check_at")
    list_filter = ("status",)
    search_fields = ("name", "integration__name")


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ("connection", "direction", "status", "occurred_at")
    list_filter = ("direction", "status")
    search_fields = ("payload_ref", "connection__name")


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "status")
    list_filter = ("status",)
    search_fields = ("name", "url")
