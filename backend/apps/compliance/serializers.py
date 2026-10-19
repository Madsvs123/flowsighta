from rest_framework import serializers

from apps.compliance.models import (
    ComplianceAssessment,
    ComplianceCertificate,
    ComplianceRequirement,
    RegulatoryUpdate,
)
from apps.core.mixins import TenantSerializer


class ComplianceRequirementSerializer(TenantSerializer):
    class Meta:
        model = ComplianceRequirement
        fields = ("id", "name", "category", "applies_to", "description", "created_at")
        read_only_fields = ("id", "created_at")


class ComplianceCertificateSerializer(TenantSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    requirement_name = serializers.CharField(source="requirement.name", read_only=True)

    class Meta:
        model = ComplianceCertificate
        fields = (
            "id",
            "supplier",
            "supplier_name",
            "requirement",
            "requirement_name",
            "number",
            "expires_date",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ComplianceAssessmentSerializer(TenantSerializer):
    certificate_number = serializers.CharField(source="certificate.number", read_only=True)
    assessor_name = serializers.CharField(source="assessor.get_full_name", read_only=True)

    class Meta:
        model = ComplianceAssessment
        fields = (
            "id",
            "certificate",
            "certificate_number",
            "date",
            "result",
            "notes",
            "assessor",
            "assessor_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class RegulatoryUpdateSerializer(TenantSerializer):
    class Meta:
        model = RegulatoryUpdate
        fields = ("id", "title", "region", "effective_date", "summary", "status", "created_at")
        read_only_fields = ("id", "created_at")
