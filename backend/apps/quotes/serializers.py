from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.quotes.models import QuoteConversion, QuoteLine, QuoteRevision, SalesQuote


class SalesQuoteSerializer(TenantSerializer):
    class Meta:
        model = SalesQuote
        fields = (
            "id",
            "number",
            "customer_ref",
            "status",
            "valid_until",
            "subtotal",
            "total",
            "currency",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class QuoteLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    quote_number = serializers.CharField(source="quote.number", read_only=True)

    class Meta:
        model = QuoteLine
        fields = (
            "id",
            "quote",
            "quote_number",
            "product",
            "sku",
            "product_name",
            "quantity",
            "unit_price",
            "line_total",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class QuoteRevisionSerializer(TenantSerializer):
    quote_number = serializers.CharField(source="quote.number", read_only=True)
    revised_by_name = serializers.CharField(source="revised_by.get_fullname", read_only=True)

    class Meta:
        model = QuoteRevision
        fields = (
            "id",
            "quote",
            "quote_number",
            "version",
            "notes",
            "total",
            "revised_by",
            "revised_by_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class QuoteConversionSerializer(TenantSerializer):
    quote_number = serializers.CharField(source="quote.number", read_only=True)

    class Meta:
        model = QuoteConversion
        fields = (
            "id",
            "quote",
            "quote_number",
            "sales_order_ref",
            "converted_at",
        )
        read_only_fields = ("id", "converted_at")
