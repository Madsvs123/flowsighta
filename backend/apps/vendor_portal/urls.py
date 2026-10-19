from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.vendor_portal.views import (
    PortalDocumentViewSet,
    PortalMessageViewSet,
    PortalUserViewSet,
)

router = DefaultRouter()
router.register("portal-users", PortalUserViewSet, basename="portal-user")
router.register("documents", PortalDocumentViewSet, basename="portal-document")
router.register("messages", PortalMessageViewSet, basename="portal-message")

urlpatterns = [
    path("vendor_portal/", include(router.urls)),
]
