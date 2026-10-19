from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.core.services import next_number
from apps.procurement.models import (
    ApprovalStep,
    Backorder,
    GoodsReceipt,
    PurchaseOrder,
    PurchaseOrderLine,
    Requisition,
    RequisitionLine,
)
from apps.procurement.serializers import (
    ApprovalStepSerializer,
    BackorderSerializer,
    GoodsReceiptSerializer,
    PurchaseOrderLineSerializer,
    PurchaseOrderSerializer,
    RequisitionLineSerializer,
    RequisitionSerializer,
)
from apps.procurement.services import (
    cancel_purchase_order,
    convert_requisition,
    decide_approval,
    issue_purchase_order,
    post_goods_receipt,
    record_po_status,
    submit_requisition,
)
from apps.suppliers.models import Supplier


class RequisitionViewSet(TenantViewSet):
    queryset = Requisition.objects.select_related("requester", "warehouse").prefetch_related("lines", "approvals")
    serializer_class = RequisitionSerializer
    required_permission = "procurement.view"
    write_permission = "procurement.create"
    search_fields = ["number", "titel"]
    filterset_fields = ["status", "warehouse", "requester"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            requester=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
            number=next_number(Requisition, self.request.organization, "REQ"),
        )

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        req = submit_requisition(self.get_object(), request.user)
        return Response(self.get_serializer(req).data)

    @action(detail=True, methods=["post"], url_path="convert")
    def convert(self, request, pk=None):
        supplier_id = request.data.get("supplier_id")
        supplier = Supplier.objects.filter(organization=request.organization, id=supplier_id).first()
        po = convert_requisition(self.get_object(), supplier, request.user)
        return Response(PurchaseOrderSerializer(po, context={"request": request}).data)


class RequisitionLineViewSet(TenantViewSet):
    queryset = RequisitionLine.objects.select_related("requisition")
    serializer_class = RequisitionLineSerializer
    required_permission = "procurement.view"
    write_permission = "procurement.create"
    filterset_fields = ["requisition"]


class ApprovalStepViewSet(TenantViewSet):
    queryset = ApprovalStep.objects.select_related("requisition", "approver")
    serializer_class = ApprovalStepSerializer
    required_permission = "procurement.view"
    write_permission = "procurement.approve"
    filterset_fields = ["requisition", "status"]

    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        step = self.get_object()
        decide_approval(step, request.user, bool(request.data.get("approve")), request.data.get("comment", ""))
        return Response(self.get_serializer(step).data



class PurchaseOrderViewSet(TenantViewSet):
    queryset = PurchaseOrder.objects.select_related("supplier", "warehouse").prefetch_related("lines", "status_history")
    serializer_class = PurchaseOrderSerializer
    required_permission = "procurement.view"
    write_permission = "procurement.create"
    search_fields = ["number", "supplier__name", "notes"]
    filterset_fields = ["status", "supplier", "warehouse"]
    ordering_fields = ["created_at", "expected_delivery_date", "total_amount"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
            number=next_number(PurchaseOrder, self.request.organization, "PO"),
        )

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        po = issue_purchase_order(self.get_object(), request.user)
        return Response(self.get_serializer(po).data)

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        po = self.get_object()
        po.acknowledged_at = po.acknowledged_at or __import__("django.utils.timezone", fromlist=["timezone"]).now()
        po.save(update_fields=["acknowledged_at"])
        record_po_status(po, PurchaseOrder.Status.ACKNOWLEDGED, request.user)
        return Response(self.get_serializer(po).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        po = cancel_purchase_order(self.get_object(), request.user, request.data.get("reason", ""))
        return Response(self.get_serializer(po).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        po = self.get_object()
        po.closed_at = __import__("django.utils.timezone", fromlist=["timezone"]).now()
        po.save(update_fields=["closed_at"])
        record_po_status(po, PurchaseOrder.Status.CLOSED, request.user)
        return Response(self.get_serializer(po).data)


class PurchaseOrderLineViewSet(TenantViewSet):
    queryset = PurchaseOrderLine.objects.select_related("purchase_order")
    serializer_class = PurchaseOrderLineSerializer
    required_permission = "procurement.view"
    write_permission = "procurement.create"
    filterset_fields = ["purchase_order", "sku"]


class GoodsReceiptViewSet(TenantViewSet):
    queryset = GoodsReceipt.objects.select_related("purchase_order", "warehouse").prefetch_related("lines")
    serializer_class = GoodsReceiptSerializer
    required_permission = "procurement.view"
    write_permission = "procurement.receive"
    search_fields = ["number", "packing_slip"]
    filterset_fields = ["status", "warehouse", "purchase_order"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
            number=next_number(GoodsReceipt, self.request.organization, "GRN"),
        )

    @action(detail=True, methods=["post"])
    def post(self, request, pk=None):
        receipt = post_goods_receipt(self.get_object(), request.user)
        return Response(self.get_serializer(receipt).data)


class BackorderViewSet(TenantViewSet):
    queryset = Backorder.objects.select_related("purchase_order", "po_line")
    serializer_class = BackorderSerializer
    required_permission = "procurement.view"
    write_permission = "procurement.create"
    filterset_fields = ["status", "purchase_order"]
