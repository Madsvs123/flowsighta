from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.vendor_portal.models import PortalDocument, PortalMessage, PortalUser
from apps.vendor_portal.serializers import (
    PortalDocumentSerializer,
    PortalMessageSerializer,
    PortalUserSerializer,
)


class PortalUserViewSet(TenantViewSet):
    queryset = PortalUser.objects.select_related("supplier", "user")
    serializer_class = PortalUserSerializer
    required_permission = "vendor_portal.view"
    write_permission = "vendor_portal.manage"
    search_fields = ["supplier__name", "user__email", "user__first_name", "user__last_name"]
    filterset_fields = ["supplier", "role", "is_active"]

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        portal_user = self.get_object()
        portal_user.is_active = True
        portal_user.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(portal_user).data)


class PortalDocumentViewSet(TenantViewSet):
    queryset = PortalDocument.objects.select_related("supplier")
    serializer_class = PortalDocumentSerializer
    required_permission = "vendor_portal.view"
    write_permission = "vendor_portal.manage"
    search_fields = ["title", "supplier__name"]
    filterset_fields = ["supplier", "type", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        users = PortalUser.objects.filter(organization=request.organization)
        messages = PortalMessage.objects.filter(organization=request.organization)
        return Response(
            {
                "document_count": qs.count(),
                "pending_documents": qs.filter(status=PortalDocument.Status.PENDING).count(),
                "approved_documents": qs.filter(status=PortalDocument.Status.APPROVED).count(),
                "rejected_documents": qs.filter(status=PortalDocument.Status.REJECTED).count(),
                "portal_users": users.count(),
                "active_portal_users": users.filter(is_active=True).count(),
                "message_count": messages.count(),
                "unread_messages": messages.filter(is_read=False).count(),
                "documents_by_type": {
                    t: qs.filter(type=t).count() for t, _ in PortalDocument.Type.choices
                },
            }
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        document = self.get_object()
        document.status = PortalDocument.Status.APPROVED
        document.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(document).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        document = self.get_object()
        document.status = PortalDocument.Status.REJECTED
        document.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(document).data)


class PortalMessageViewSet(TenantViewSet):
    queryset = PortalMessage.objects.select_related("supplier")
    serializer_class = PortalMessageSerializer
    required_permission = "vendor_portal.view"
    write_permission = "vendor_portal.manage"
    search_fields = ["subject", "body", "supplier__name"]
    filterset_fields = ["supplier", "direction", "is_read"]

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.save(update_fields=["is_read", "updated_at"])
        return Response(self.get_serializer(message).data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        updated = self.get_queryset().filter(is_read=False).update(
            is_read=True, updated_by=request.user
        )
        return Response({"marked_read": updated})
