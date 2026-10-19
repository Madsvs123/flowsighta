from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.customs.models import ComplianceRule, CustomsDeclaration, CustomsDocument, HsCode


class HsCodeSerializer(TenantSerializer):
    class Meta:
        model = HsCode
        fields = ("id", "code", "description", "duty_rate", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class CustomsDeclarationSerializer(TenantSerializer):
    hs_code_code = serializers.CharField(source="hs_code.code", read_only=True)
    hs_code_description = serializers.CharField(source="hs_code.description", read_only=True)

    class Meta:
        model = CustomsDeclaration
        fields = (
            "id",
            "number",
            "shipment_ref",
            "hs_code",
            "hs_code_code",
            "hs_code_description",
            "origin_country",
            "destination_country",
            "declared_value",
            "currency",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CustomsDocumentSerializer(TenantSerializer):
    declaration_number = serializers.CharField(source="declaration.ref", read_only=True)

    class Meta:
        model = CustomsDocument
        fields = (
            "id",
            "declaration",
            "declaration_number",
            "type",
            "title",
            "file",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ComplianceRuleSerializer(TenantSerializer):
    class Meta:
        model = ComplianceRule
        fields = (
            "id",
            "country",
            "category",
            "restriction",
            "description",
            "effective_from",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
