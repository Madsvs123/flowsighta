from django.utils import timezone
from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.rfq.models import Rfq, RfqLine, RfqResponse, RfqResponseLine


class RfqLineSerializer(TenantSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = RfqLine
        fields = (
            "id",
            "rfq",
            "product",
            "product_name",
            "quantity",
            "target_price",
            "line_total",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class RfqResponseLineSerializer(TenantSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = RfqResponseLine
        fields = (
            "id",
            "response",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "delivery_days",
            "incoterm",
            "line_total",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class RfqResponseSerializer(TenantSerializer):
    lines = RfqResponseLineSerializer(many=True, required=False)
    rfq_number = serializers.CharField(source="rfq.number", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    response_total = serializers.SerializerMethodField()

    class Meta:
        model = RfqResponse
        fields = (
            "id",
            "rfq",
            "rfq_number",
            "supplier",
            "supplier_name",
            "status",
            "submitted_at",
            "response_total",
            "lines",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "submitted_at", "created_at", "updated_at")

    def get_response_total(self, obj):
        return sum((line.line_total for line in obj.lines.all()), 0)

    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        instance = super().create(validated_data)
        for line in lines:
            line.pop("response", None)
            RfqResponseLine.objects.create(organization=instance.organization, response=instance, **line)
        return instance


class RfqSerializer(TenantSerializer):
    lines = RfqLineSerializer(many=True, required=False)
    responses = RfqResponseSerializer(many=True, read_only=True)
    line_count = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()
    target_value = serializers.SerializerMethodField()

    class Meta:
        model = Rfq
        fields = (
            "id",
            "number",
            "title",
            "status",
            "due_date",
            "notes",
            "line_count",
            "response_count",
            "target_value",
            "lines",
            "responses",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "number", "status", "lines", "created_at", "updated_at")

    def get_line_count(self, obj):
        return getattr(obj, "_line_count", None) or obj.lines.count()

    def get_response_count(self, obj):
        return getattr(obj, "_response_count", None) or obj.responses.count()

    def get_target_value(self, obj):
        return sum((line.line_total for line in obj.lines.all()), 0

    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        instance = super().create(validated_data)
        for line in lines:
            line.pop("rfq", None)
            RfqLine.objects.create(organization=instance.organization, rfq=instance, **line)
        return instance
