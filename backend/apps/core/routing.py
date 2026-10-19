from django.urls import path

from apps.core.consumers import OrganizationConsumer

websocket_urlpatterns = [
    path("ws/orgz/", OrganizationConsumer.as_asgi()
]
