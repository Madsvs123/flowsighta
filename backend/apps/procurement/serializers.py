from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.procurement.models import (
    ApprovalStep,
    Backorder,
    GoodsReceipt,
    GoodsReceiptLine,
    POStatusHistory,
    PurchaseOrder,
    PurchaseOrderLine,
    Requisition,
    RequisitionLine,
)


class RequisitionLineSerializer(TenantSerializer):
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = RequisitionLine
        fields = (
            "id",
            "requisition",
            "sku",
            "description",
            "quantity",
            "uom",
            "estimated_unit_price",
            "suggested_supplier",
            "needed_by",
            "line_total",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ApprovalStepSerializer(TenantSerializer):
    approver_name = serializers.CharField(source="approver.full_name", read_only=True)

    class Meta:
        model = ApprovalStep
        fields = (
            "id",
            "requisition",
            "sequence",
            "approver",
            "approver_name",
            "approver_role",
            "status",
            "decided_at",
            "comment",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "decided_at")


class RequisitionSerializer(TenantSerializer):
    lines = RequisitionLineSerializer(many=True, required=False)
    approvals = ApprovalStepSerializer(many=True, read_only=True)
    requester_name = serializers.CharField(source="requester.full_name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = Requisition
        fields = (
            "id",
            "number",
            "title",
            "status",
            "requester",
            "requester_name",
            "warehouse",
            "warehouse_name",
            "needed_by",
            "justification",
            "total_amount",
            "currency",
            "lines",
            "approvals",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "number", "total_amount", "created_at", "updated_at")

    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        instance = super().create(validated_data)
        total = Decimal("0")
        for line in lines:
            obj = RequisitionLine.objects.create(organization=instance.organization, requisition=instance, **line)
            total += Decimal(str(obj.quantity))
        instance.total_amount = total + Decimal("0")
        instance.save(update_fields=["total_amount"])
        return instance


class PurchaseOrderLineSerializer(TenantSerializer):
    quantity_open = serializers.ReadOnlyField()
    line_total = serializers.ReadOnlyField()
    fulfillment_status = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseOrderLine
        fields = (
            "id",
            "purchase_order",
            "sku",
            "description",
            "quantity_ordered",
            "quantity_received",
            "quantity_cancelled",
            "quantity_backordered",
            "uom",
            "unit_price",
            "expected_delivery_date",
            "warehouse",
            "product",
            "quantity_open",
            "line_total",
            "fulfillment_status",
            "created_at",
        )
        read_only_fields = ("id", "quantity_received", "quantity_cancelled", "quantity_backordered", "created_at")


class POStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.full_name", read_only=True)

    class Meta:
        model = POStatusHistory
        fields = ("id", "from_status", "to_status", "note", "changed_by", "changed_by_name", "created_at")


class PurchaseOrderSerializer(TenantSerializer):
    lines = PurchaseOrderLineSerializer(many=True, required=False)
    status_history = POStatusHistorySerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = (
            "id",
            "number",
            "requisition",
            "supplier",
            "supplier_name",
            "warehouse",
            "warehouse_name",
            "status",
            "currency",
            "payment_terms",
            "incoterms",
            "expected_delivery_date",
            "issued_at",
            "acknowledged_at",
            "closed_at",
            "cancelled_at",
            "cancellation_reason",
            "subtotal",
            "tax_amount",
            "freight_amount",
            "total_amount",
            "notes",
            "lines",
            "status_history",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "number",
            "status",
            "issued_at",
            "acknowledged_at",
            "closed_at",
            "cancelled_at",
            "subtotal",
            "total_amount",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        instance = super().create(validated_data)
        subtotal = Decimal("0")
        for line in lines:
            obj = PurchaseOrderLine.objects.create(organization=instance.organization, purchase_order=instance, **line)
            subtotal += Decimal(str(obj.line_total))
        instance.subtotal = subtotal
        instance.total_amount = subtotal + instance.freight_amount
        instance.save(update_fields=["subtotal", "total_amount"])
        return instance


class GoodsReceiptLineSerializer(TenantSerializer):
    class Meta:
        model = GoodsReceiptLine
        fields = ("id", "receipt", "po_line", "quantity", "quantity_damaged", "batch_number", "location", "created_at")
        read_only_fields = ("id", "created_at")


class GoodsReceiptSerializer(TenantSerializer):
    lines = GoodsReceiptLineSerializer(many=True, required=False)
    purchase_order_number = serializers.CharField(source="purchase_order.number", read_only=True)

    class Meta:
        model = GoodsReceipt
        fields = (
            "id",
            "number",
            "purchase_order",
            "purchase_order_number",
            "warehouse",
            "status",
            "received_at",
            "packing_slip",
            "notes",
            "lines",
            "created_at",
        )
        read_only_fields = ("id", "number", "status", "received_at", "created_at")

    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        instance = super().create(validated_data)
        for line in lines:
            GoodsReceiptLine.objects.create(organization=instance.organization, receipt=instance, **line)
        return instance


class BackorderSerializer(TenantSerializer):
    class Meta:
        model = Backorder
        fields = (
            "id",
            "purchase_order",
            "po_line",
            "quantity",
            "promised_date",
            "status",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
