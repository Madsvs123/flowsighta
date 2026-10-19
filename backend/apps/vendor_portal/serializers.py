from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.vendor_portal.models import PortalDocument, PortalMessage, PortalUser


class PortalUserSerializer(TenantSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = PortalUser
        fields = (
            "id",
            "supplier",
            "supplier_name",
            "user",
            "user_email",
            "user_name",
            "role",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_user_name(self, obj):
        return obj.user.full_name if obj.user_id else ""


class PortalDocumentSerializer(TenantSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = PortalDocument
        fields = (
            "id",
            "supplier",
            "supplier_name",
            "type",
            "title",
            "file",
            "status",
            "uploaded_at",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")


class PortalMessageSerializer(TenantSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = PortalMessage
        fields = (
            "id",
            "supplier",
            "supplier_name",
            "subject",
            "body",
            "direction",
            "is_read",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
