from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.invoicing.models import CreditNote, CustomerInvoice, InvoiceLine


class InvoiceLineSerializer(TenantSerializer):
    class Meta:
        model = InvoiceLine
        fields = (
            "id",
            "invoice",
            "description",
            "quantity",
            "rate",
            "tax_pct",
            "line_total",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CustomerInvoiceSerializer(TenantSerializer):
    line_count = serializers.SerializerMethodField()
    credit_notes_total = serializers.SerializerMethodField()

    class Meta:
        model = CustomerInvoice
        fields = (
            "id",
            "number",
            "customer_ref",
            "status",
            "issue_date",
            "due_date",
            "subtotal",
            "tax_total",
            "total",
            "currency",
            "line_count",
            "credit_notes_total",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_line_count(self, obj):
        return obj.lines.count()

    def get_credit_notes_total(self, obj):
        return float(sum((c.amount or 0) for c in obj.credit_notes.all()))


class CreditNoteSerializer(TenantSerializer):
    invoice_number = serializers.CharField(source="invoice__number", read_only=True)

    class Meta:
        model = CreditNote
        fields = (
            "id",
            "invoice",
            "invoice_number",
            "number",
            "reason",
            "amount",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
