from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.uom.models import Uom, UomConversion


class UomSerializer(TenantSerializer):
    class Meta:
        model = Uom
        fields = ("id", "code", "dimension", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class UomConversionSerializer(TenantSerializer):
    from_uom_code = serializers.CharField(source="from_uom.code", read_only=True)
    from_uom_name = serializers.CharField(source="from_uom.name", read_only=True)
    to_uom_code = serializers.CharField(source="to_uom.code", read_only=True)
    to_uom_name = serializers.CharField(source="to_uom.name", read_only=True)

    class Meta:
        model = UomConversion
        fields = (
            "id",
            "from_uom",
            "from_uom_code",
            "from_uom_name",
            "to_uom",
            "to_uom_code",
            "to_uom_name",
            "factor",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
