from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.payments.models import Payment, PaymentAllocation, PaymentRun, PaymentTerm


class PaymentSerializer(TenantSerializer):
    allocation_total = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "reference",
            "invoice_ref",
            "amount",
            "method",
            "status",
            "paid_at",
            "allocation_total",
            "created_at",
        )
        read_only_fields = ("id",)

    def get_allocation_total(self, obj):
        return float(sum((a.amount or 0) for a in obj.allocations.all()))


class PaymentTermSerializer(TenantSerializer):
    class Meta:
        model = PaymentTerm
        fields = ("id", "name", "days", "discount_pct", "is_default", "created_at")
        read_only_fields = ("id", "created_at")


class PaymentRunSerializer(TenantSerializer):
    class Meta:
        model = PaymentRun
        fields = ("id", "number", "status", "executed_at", "total", "created_at")
        read_only_fields = ("id", "created_at")


class PaymentAllocationSerializer(TenantSerializer):
    payment_reference = serializers.CharField(source="payment.reference", read_only=True)

    class Meta:
        model = PaymentAllocation
        fields = (
            "id",
            "payment",
            "payment_reference",
            "invoice_ref",
            "amount",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
