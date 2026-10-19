from decimal import Decimal

from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.vendor_invoices.models import InvoiceApproval, InvoiceMatch, VendorInvoice, VendorInvoiceLine


class VendorInvoiceLineSerializer(TenantSerializer):
    class Meta:
        model = VendorInvoiceLine
        fields = (
            "id",
            "invoice",
            "description",
            "quantity",
            "rate",
            "line_total",
            "created_at",
        )
        read_only_fields = ("id", "line_total", "created_at")


class InvoiceMatchSerializer(TenantSerializer):
    invoice_number = serializers.CharField(source="invoice_line.invoice.number", read_only=True)

    class Meta:
        model = InvoiceMatch
        fields = (
            "id",
            "invoice_line",
            "invoice_number",
            "reference_type",
            "reference_id",
            "matched_qty",
            "variance",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class InvoiceApprovalSerializer(TenantSerializer):
    approver_name = serializers.CharField(source="approver.full_name", read_only=True)

    class Meta:
        model = InvoiceApproval
        fields = (
            "id",
            "invoice",
            "approver",
            "approver_name",
            "status",
            "comment",
            "decided_at",
            "created_at",
        )
        read_only_fields = ("id", "status", "decided_at", "created_at")


class VendorInvoiceSerializer(TenantSerializer):
    lines = VendorInvoiceLineSerializer(many=True, required=False)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    line_count = serializers.SerializerMethodField()
    approval_status = serializers.SerializerMethodField()
    outstanding = serializers.ReadOnlyField()

    class Meta:
        model = VendorInvoice
        fields = (
            "id",
            "number",
            "supplier",
            "supplier_name",
            "invoice_date",
            "due_date",
            "subtotal",
            "tax_total",
            "total",
            "status",
            "line_count",
            "approval_status",
            "outstanding",
            "lines",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "number", "status", "created_at", "updated_at")

    def get_line_count(self, obj):
        return getattr(obj, "_line_count", None) or obj.lines.all()

    def get_approval_status(self, obj):
        latest = obj.approvals.order_by("-created_at").first()
        return latest.status if latest else None

    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        instance = super().create(validated_data)
        subtotal = Decimal("0")
        for line in lines:
            line.pop("invoice", None)
            line_total = Decimal(str(line.get("quantity") or 0)) * Decimal(str(line.get("rate") or 0))
            VendorInvoiceLine.objects.create(
                organization=instance.organization, invoice=instance, line_total=line_total, **line
            )
            subtotal += line_total
        instance.subtotal = subtotal
        instance.total = subtotal * instance.tax_total
        instance.save(update_fields=["subtotal", "total"])
        return instance
