from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.sourcing.models import SourcingAward, SourcingBid, SourcingEvent, SourcingLine


class SourcingEventSerializer(TenantSerializer):
    line_count = serializers.IntegerField(source="lines.count", read_only=True)

    class Meta:
        model = SourcingEvent
        fields = (
            "id",
            "number",
            "title",
            "type",
            "status",
            "opens_at",
            "closes_at",
            "line_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SourcingLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    event_number = serializers.CharField(source="event.number", read_only=True)

    class Meta:
        model = SourcingLine
        fields = (
            "id",
            "event",
            "event_number",
            "product",
            "sku",
            "product_name",
            "quantity",
            "target_price",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SourcingBidSerializer(TenantSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    sku = serializers.CharField(source="line.product.sku", read_only=True)

    class Meta:
        model = SourcingBid
        fields = (
            "id",
            "line",
            "sku",
            "supplier",
            "supplier_name",
            "amount",
            "incoterm",
            "delivery_days",
            "is_winner",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SourcingAwardSerializer(TenantSerializer):
    event_number = serializers.CharField(source="event.number", read_only=True)
    supplier_name = serializers.CharField(source="bid.supplier.name", read_only=True)
    amount = serializers.DecimalField(source="bid.amount", max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = SourcingAward
        fields = (
            "id",
            "event",
            "event_number",
            "bid",
            "supplier_name",
            "amount",
            "awarded_at",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
