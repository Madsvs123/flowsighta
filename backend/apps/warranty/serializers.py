from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.warranty.models import (
    ClaimResolution,
    WarrantyClaim,
    WarrantyPlan,
    WarrantyRegistration,
)


class WarrantyPlanSerializer(TenantSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = WarrantyPlan
        fields = (
            "id",
            "product",
            "product_sku",
            "product_name",
            "duration_months",
            "coverage",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class WarrantyRegistrationSerializer(TenantSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    serial_number = serializers.CharField(source="serial.serial", read_only=True)
    claim_count = serializers.SerializerMethodField()

    class Meta:
        model = WarrantyRegistration
        fields = (
            "id",
            "customer_ref",
            "product",
            "product_sku",
            "product_name",
            "serial",
            "serial_number",
            "start_date",
            "end_date",
            "status",
            "claim_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_claim_count(self, obj):
        return obj.claims.count()


class WarrantyClaimSerializer(TenantSerializer):
    customer_ref = serializers.CharField(source="registration.customer_ref", read_only=True)
    product_name = serializers.CharField(source="registration.product.name", read_only=True)
    resolution_count = serializers.SerializerMethodField()

    class Meta:
        model = WarrantyClaim
        fields = (
            "id",
            "registration",
            "customer_ref",
            "product_name",
            "status",
            "date",
            "description",
            "resolution_count",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")

    def get_resolution_count(self, obj):
        return obj.resolutions.count()


class ClaimResolutionSerializer(TenantSerializer):
    claim_status = serializers.CharField(source="claim.registration.status", read_only=True)

    class Meta:
        model = ClaimResolution
        fields = (
            "id",
            "claim",
            "claim_status",
            "type",
            "notes",
            "cost",
            "resolved_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
