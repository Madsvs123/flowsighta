from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.taxation.models import TaxCode, TaxRate, TaxRule


class TaxCodeSerializer(TenantSerializer):
    rate_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = TaxCode
        fields = ("id", "code", "name", "description", "rate_count", "created_at")
        read_only_fields = ("id", "created_at")


class TaxRateSerializer(TenantSerializer):
    tax_code_code = serializers.CharField(source="tax_code.code", read_only=True)
    tax_code_name = serializers.CharField(source="tax_code.name", read_only=True)

    class Meta:
        model = TaxRate
        fields = (
            "id",
            "tax_code",
            "tax_code_code",
            "tax_code_name",
            "jurisdiction",
            "rate",
            "effective_from",
            "effective_to",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "tax_code")


class TaxRuleSerializer(TenantSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    tax_code_code = serializers.CharField(source="tax_code.code", read_only=True)

    class Meta:
        model = TaxRule
        fields = (
            "id",
            "name",
            "product",
            "product_name",
            "product_sku",
            "category",
            "tax_code",
            "tax_code_code",
            "applies_from",
            "applies_to",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
