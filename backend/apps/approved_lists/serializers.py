from rest_framework import serializers

from apps.approved_lists.models import ApprovedList, ApprovedSupplier
from apps.core.mixins import TenantSerializer


class ApprovedListSerializer(TenantSerializer):
    supplier_count = serializers.IntegerField(source="approved_suppliers.count", read_only=True)
    approved_count = serializers.SerializerMethodField()

    class Meta:
        model = ApprovedList
        fields = (
            "id",
            "name",
            "category",
            "status",
            "description",
            "supplier_count",
            "approved_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_approved_count(self, obj)
        return obj.approved_suppliers.filter(status=ApprovedSupplier.Status.PENDING).count()


class ApprovedSupplierSerializer(TenantSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    supplier_code = serializers.CharField(source="supplier.code", read_only=True)
    list_name = serializers.CharField(source="list.name", read_only=True)

    class Meta:
        model = ApprovedSupplier
        fields = (
            "id",
            "list",
            "list_name",
            "supplier",
            "supplier_name",
            "supplier_code",
            "rating",
            "status",
            "notes",
            "approved_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
