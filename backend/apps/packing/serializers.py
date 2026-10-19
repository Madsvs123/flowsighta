from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.packing.models import Box, PackedItem, PackingSession


class PackingSessionSerializer(TenantSerializer):
    shipment_number = serializers.CharField(source="shipment.number", read_only=True)
    packed_by_email = serializers.CharField(source="packed_by.email", read_only=True)
    box_count = serializers.IntegerField(read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PackingSession
        fields = (
            "id",
            "number",
            "shipment",
            "shipment_number",
            "status",
            "packed_by",
            "packed_by_email",
            "box_count",
            "item_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at")


class BoxSerializer(TenantSerializer):
    session_number = serializers.CharField(source="session.number", read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Box
        fields = (
            "id",
            "session",
            "session_number",
            "code",
            "weight",
            "dims",
            "is_sealed",
            "item_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PackedItemSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    box_code = serializers.CharField(source="box.code", read_only=True)

    class Meta:
        model = PackedItem
        fields = (
            "id",
            "box",
            "box_code",
            "product",
            "sku",
            "product_name",
            "quantity",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
