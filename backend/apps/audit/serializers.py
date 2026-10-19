from rest_framework import serializers

from apps.audit.models import AuditAction, AuditEngagement, AuditFinding, AuditProgram
from apps.core.mixins import TenantSerializer


class AuditProgramSerializer(TenantSerializer):
    class Meta:
        model = AuditProgram
        fields = ("id", "name", "period", "status", "created_at")
        read_only_fields = ("id", "created_at")


class AuditEngagementSerializer(TenantSerializer):
    program_name = serializers.CharField(source="program.period", read_only=True)
    auditor_name = serializers.CharField(source="auditor.get_full_name", read_only=True)

    class Meta:
        model = AuditEngagement
        fields = (
            "id",
            "program",
            "program_name",
            "scope",
            "auditor",
            "auditor_name",
            "start_date",
            "end_date",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class AuditFindingSerializer(TenantSerializer):
    engagement_scope = serializers.CharField(source="engagement.scope", read_only=True)
    program_name = serializers.CharField(source="engagement.program.name", read_only=True)

    class Meta:
        model = AuditFinding
        fields = (
            "id",
            "engagement",
            "engagement_scope",
            "program_name",
            "severity",
            "description",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class AuditActionSerializer(TenantSerializer):
    finding_description = serializers.CharField(source="finding.description", read_only=True)
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)

    class Meta:
        model = AuditAction
        fields = (
            "id",
            "finding",
            "finding_description",
            "action",
            "owner",
            "owner_name",
            "due_date",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
