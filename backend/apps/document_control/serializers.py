from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.document_control.models import (
    Document,
    DocumentApproval,
    DocumentLink,
    DocumentRevision,
)


class DocumentSerializer(TenantSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    latest_version = serializers.CharField(source="revisions.first.version", read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "code",
            "title",
            "type",
            "status",
            "owner",
            "owner_name",
            "latest_version",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class DocumentRevisionSerializer(TenantSerializer):
    document_code = serializers.CharField(source="document.code", read_only=True)
    document_title = serializers.CharField(source="document.title", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)

    class Meta:
        model = DocumentRevision
        fields = (
            "id",
            "document",
            "document_code",
            "document_title",
            "version",
            "file",
            "notes",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class DocumentApprovalSerializer(TenantSerializer):
    revision_version = serializers.CharField(source="revision.version", read_only=True)
    document_code = serializers.CharField(source="revision.document.code", read_only=True)
    approver_name = serializers.CharField(source="approver.email", read_only=True)

    class Meta:
        model = DocumentApproval
        fields = (
            "id",
            "revision",
            "revision_version",
            "document_code",
            "approver",
            "approver_name",
            "decision",
            "comment",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class DocumentLinkSerializer(TenantSerializer):
    document_code = serializers.CharField(source="document.code", read_only=True)
    document_title = serializers.CharField(source="document.title", read_only=True)

    class Meta:
        model = DocumentLink
        fields = (
            "id",
            "document",
            "document_code",
            "document_title",
            "object_type",
            "object_id",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
