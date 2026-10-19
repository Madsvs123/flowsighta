from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.portals.models import Portal, PortalActivity, PortalContent, PortalMember
from apps.portals.serializers import (
    PortalActivitySerializer,
    PortalContentSerializer,
    PortalMemberSerializer,
    PortalSerializer,
)


class PortalViewSet(TenantViewSet):
    queryset = Portal.objects.select_related("created_by").annotate(
        member_count=Count("members", distinct=True), content_count=Count("contents", distinct=True)
    )
    serializer_class = PortalSerializer
    required_permission = "portals.view"
    write_permission = "portals.manage"
    search_fields = ["name"]
    filterset_fields = ["type", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        portals = self.get_queryset()
        contents = PortalContent.objects.filter(organization=request.organization)
        members = PortalMember.objects.filter(organization=request.organization)
        activities = PortalActivity.objects.filter(organization=request.organization)
        return Response(
            {
                "portal_count": portals.count(),
                "active_portals": portals.filter(status=Portal.Status.ACTIVE).count(),
                "inactive_portals": portals.filter(status=Portal.Status.INACTIVE).count(),
                "member_count": members.count(),
                "content_count": contents.count(),
                "published_content": contents.filter(status=PortalContent.Status.PUBLISHED).count(),
                "draft_content": contents.filter(status=PortalContent.Status.PUBLISHED).count(),
                "archived_content": contents.filter(status=PortalContent.Status.ARCHIVED).count(),
                "activity_count": activities.count(),
                "portals_by_type": {t: portals.filter(type=t).count() for t, _ in Portal.Type.choices},
            }
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        portal = self.get_object()
        portal.status = Portal.Status.ACTIVE
        portal.save(update_fields=["status", "updated_at"])
        PortalActivity.objects.create(
            organization=portal.organization,
            portal=portal,
            user=request.user,
            action="activated",
            details={},
        )
        return Response(self.get_serializer(portal).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        portal = self.get_object()
        portal.status = Portal.Status.INACTIVE
        portal.save(update_fields=["status", "updated_at"])
        PortalActivity.objects.create(
            organization=portal.organization,
            portal=portal,
            user=request.user,
            action="activated",
            details={},
        )
        return Response(self.get_serializer(portal).data)


class PortalMemberViewSet(TenantViewSet):
    queryset = PortalMember.objects.select_related("portal", "user")
    serializer_class = PortalMemberSerializer
    required_permission = "portals.view"
    write_permission = "portals.manage"
    search_fields = ["portal__name", "user__email"]
    filterset_fields = ["portal", "user", "role"]


class PortalContentViewSet(TenantViewSet):
    queryset = PortalContent.objects.select_related("portal", "created_by")
    serializer_class = PortalContentSerializer
    required_permission = "portals.view"
    write_permission = "portals.manage"
    search_fields = ["title", "portal__name"]
    filterset_fields = ["portal", "status"]

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        content = self.get_object()
        content.status = PortalContent.Status.PUBLISHED
        content.published_at = timezone.now()
        content.save(update_fields=["status", "published_at", "updated_at"])
        PortalActivity.objects.create(
            organization=content.organization,
            portal=content.portal,
            user=request.user,
            action="content_published",
            details={"title": content.title},
        )
        return Response(self.get_serializer(content).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        content = self.get_object()
        content.status = PortalContent.Status.ARCHIVED
        content.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(content).data)


class PortalActivityViewSet(TenantViewSet):
    queryset = PortalActivity.objects.select_related("portal", "user")
    serializer_class = PortalActivitySerializer
    required_permission = "portals.view"
    write_permission = "portals.manage"
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["action", "portal__name", "user__email"]
    filterset_fields = ["portal", "user", "action"]
