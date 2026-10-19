from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.suppliers.models import (
    OnboardingStep,
    PurchaseHistory,
    Supplier,
    SupplierCertification,
    SupplierContact,
    SupplierContract,
    SupplierDocument,
    SupplierProduct,
    SupplierScoreSnapshot,
)


class SupplierContactSerializer(TenantSerializer):
    class Meta:
        model = SupplierContact
        fields = ("id", "supplier", "name", "title", "email", "phone", "is_primary", "role", "created_at")
        read_only_fields = ("id", "created_at")


class SupplierContractSerializer(TenantSerializer):
    class Meta:
        model = SupplierContract
        fields = (
            "id",
            "supplier",
            "number",
            "title",
            "status",
            "start_date",
            "end_date",
            "value",
            "payment_terms",
            "incoterms",
            "auto_renew",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SupplierProductSerializer(TenantSerializer):
    class Meta:
        model = SupplierProduct
        fields = (
            "id",
            "supplier",
            "sku",
            "name",
            "description",
            "uom",
            "unit_price",
            "currency",
            "lead_time_days",
            "moq",
            "order_multiple",
            "is_active",
            "catalog_product_id",
            "created_at",

        read_only_fields = ("id", "created_at")


class SupplierCertificationSerializer(TenantSerializer):
    class Meta:
        model = SupplierCertification
        fields = (
            "id",
            "supplier",
            "name",
            "issuer",
            "certificate_number",
            "issued_on",
            "expires_on",
            "status",
            "document_url",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SupplierDocumentSerializer(TenantSerializer):
    class Meta:
        model = SupplierDocument
        fields = ("id", "supplier", "title", "doc_type", "file", "notes", "created_at")
        read_only_fields = ("id", "created_at")


class OnboardingStepSerializer(TenantSerializer):
    class Meta:
        model = OnboardingStep
        fields = (
            "id",
            "supplier",
            "sequence",
            "name",
            "description",
            "status",
            "due_date",
            "completed_at",
            "owner_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SupplierScoreSnapshotSerializer(TenantSerializer):
    class Meta:
        model = SupplierScoreSnapshot
        fields = (
            "id",
            "supplier",
            "period_start",
            "period_end",
            "on_time_delivery",
            "quality",
            "fill_rate",
            "lead_time_variance",
            "composite_score",
            "spend",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PurchaseHistorySerializer(TenantSerializer):
    class Meta:
        model = PurchaseHistory
        fields = (
            "id",
            "supplier",
            "purchase_order_number",
            "ordered_on",
            "received_on",
            "amount",
            "currency",
            "on_time",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SupplierSerializer(TenantSerializer):
    contacts = SupplierContactSerializer(many=True, read_only=True)
    onboarding_progress = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = (
            "id",
            "code",
            "name",
            "legal_name",
            "status",
            "risk_level",
            "category",
            "country",
            "city",
            "address_line1",
            "website",
            "tax_id",
            "payment_terms",
            "currency",
            "default_lead_time_days",
            "minimum_order_value",
            "performance_score",
            "on_time_delivery_rate",
            "quality_score",
            "fill_rate",
            "total_spend",
            "preferred",
            "notes",
            "contacts",
            "onboarding_progress",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "performance_score",
            "on_time_delivery_rate",
            "quality_score",
            "total_spend",
            "created_at",
            "updated_at",
        )

    def get_onboarding_progress(self, obj):
        steps = list(obj.onboarding_steps.all()) if hasattr(obj, "_prefetched_objects_cache") or True else []
        total = obj.onboarding_steps.count()
        done = obj.onboarding_steps.filter(status="pending").count()
        return {"total": total, "complete": done, "percent": round((done / total) * 100, 1) if total else 0}


class SupplierDetailSerializer(SupplierSerializer):
    contracts = SupplierContractSerializer(many=True, read_only=True)
    products = SupplierProductSerializer(many=True, read_only=True)
    certifications = SupplierCertificationSerializer(many=True, read_only=True)
    onboarding_steps = OnboardingStepSerializer(many=True, read_only=True)
    score_snapshots = SupplierScoreSnapshotSerializer(many=True, read_only=True)
    purchase_history = PurchaseHistorySerializer(many=True, read_only=True)

    class Meta(SupplierSerializer.Meta):
        fields = SupplierSerializer.Meta.fields + (
            "contracts",
            "products",
            "certifications",
            "onboarding_steps",
            "score_snapshots",
            "purchase_history",
        )
