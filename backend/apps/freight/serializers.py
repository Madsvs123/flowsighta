from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.freight.models import AccessorialCharge, FreightBill, FreightBooking, FreightQuote


class FreightQuoteSerializer(TenantSerializer):
    carrier_name = serializers.CharField(source="carrier.name", read_only=True)
    carrier_code = serializers.CharField(source="carrier.codee", read_only=True)

    class Meta:
        model = FreightQuote
        fields = (
            "id",
            "carrier",
            "carrier_name",
            "carrier_code",
            "origin",
            "destination",
            "mode",
            "rate",
            "transit_days",
            "valid_until",
            "status",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class FreightBookingSerializer(TenantSerializer):
    quote_reference = serializers.CharField(source="quote.reference", read_only=True)
    quote_origin = serializers.CharField(source="quote.origin", read_only=True)
    quote_destination = serializers.CharField(source="quote.destination", read_only=True)
    quote_rate = serializers.DecimalField(source="quote.rate", max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = FreightBooking
        fields = (
            "id",
            "quote",
            "quote_reference",
            "quote_origin",
            "quote_destination",
            "quote_rate",
            "reference",
            "status",
            "booked_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class FreightBillSerializer(TenantSerializer):
    booking_reference = serializers.CharField(source="booking.reference", read_only=True)

    class Meta:
        model = FreightBill
        fields = (
            "id",
            "booking",
            "booking_reference",
            "number",
            "amount",
            "status",
            "due_date",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class AccessorialChargeSerializer(TenantSerializer):
    booking_reference = serializers.CharField(source="booking.reference", read_only=True)

    class Meta:
        model = AccessorialCharge
        fields = ("id", "booking", "booking_reference", "type", "description", "amount", "created_at")
        read_only_fields = ("id", "created_at")
