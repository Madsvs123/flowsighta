from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.purchase_contracts.models import ContractRelease, PurchaseContract, PurchaseContractLine


class PurchaseContractLineSerializer(TenantSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseContractLine
        fields = (
            "id",
            "contract",
            "product",
            "product_name",
            "price",
            "quantity",
            "received_quantity",
            "line_total",
            "created_at",
        )
        read_only_fields = ("id", "received_quantity", "created_at")


class PurchaseContractSerializer(TenantSerializer):
    lines = PurchaseContractLineSerializer(many=True, required=False)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    line_count = serializers.SerializerMethodField()
    release_count = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseContract
        fields = (
            "id",
            "number",
            "supplier",
            "supplier_name",
            "title",
            "start_date",
            "end_date",
            "total_value",
            "status",
            "line_count",
            "release_count",
            "lines",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "number", "status", "created_at", "updated_at")

    def get_release_count(self, obj):
        return getattr(obj, "_release_count", None) or obj.lines.count()

    def get_line_count(self, obj):
        return getattr(obj, "_line_count", None) or obj.releases.count()


class ContractReleaseSerializer(TenantSerializer):
    contract_number = serializers.CharField(source="contract.number", read_only=True)

    class Meta:
        model = ContractRelease
        fields = (
            "id",
            "contract",
            "contract_number",
            "number",
            "quantity",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
