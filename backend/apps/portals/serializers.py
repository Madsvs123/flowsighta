from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.portals.models import Portal, PortalActivity, PortalContent, PortalMember


class PortalSerializer(TenantSerializer):
    member_count = serializers.IntegerField(read_only=True)
    content_count = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source="created_by.first_name", read_only=True)

    class Meta:
        model = Portal
        fields = (
            "id",
            "name",
            "type",
            "status",
            "config",
            "member_count",
            "content_count",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class PortalMemberSerializer(TenantSerializer):
    portal_name = serializers.CharField(source="portal.name", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = PortalMember
        fields = ("id", "portal", "portal_name", "user", "user_name", "role", "created_at")
        read_only_fields = ("id", "created_at")


class PortalContentSerializer(TenantSerializer):
    portal_name = serializers.CharField(source="portal.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.first_name", read_only=True)

    class Meta:
        model = PortalContent
        fields = (
            "id",
            "portal",
            "portal_name",
            "title",
            "body",
            "status",
            "published_at",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "published_at", "created_at", "updated_at")


class PortalActivitySerializer(TenantSerializer):
    portal_name = serializers.CharField(source="portal.name", read_only=True)
    user_name = serializers.CharField(source="user.first_name", read_only=True)

    class Meta:
        model = PortalActivity
        fields = (
            "id",
            "portal",
            "portal_name",
            "user",
            "user_name",
            "action",
            "details",
            "occurred_at",
        )
        read_only_fields = ("id", "occurred_at")
