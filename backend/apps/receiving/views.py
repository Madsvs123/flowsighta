from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.core.services import next_number
from apps.receiving.models import PutawayTask, Receipt, ReceiptLine
from apps.receiving.serializers import PutawayTaskSerializer, ReceiptLineSerializer, ReceiptSerializer


class ReceiptViewSet(TenantViewSet):
    queryset = Receipt.objects.select_related("supplier", "warehouse")
    serializer_class = ReceiptSerializer
    required_permission = "receiving.view"
    write_permission = "receiving.manage"
    search_fields = ["number", "reference", "supplier__name", "warehouse__code"]
    filterset_fields = ["supplier", "warehouse", "status"]

    def perform_create(self, serializer):
        instance = serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        if not instance.number:
            instance.number = next_number(Receipt, instance.organization, "RCP")
            instance.save(update_fields=["number"])

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        lines = ReceiptLine.objects.filter(receipt__organization_id=request.organization.id)
        return Response(
            {
                "receipt_count": qs.count(),
                "expected": qs.filter(status=Receipt.Status.EXPECTED).count(),
                "in_progress": qs.filter(status=Receipt.Status.IN_PROGRESS).count(),
                "received": qs.filter(status=Receipt.Status.RECEIVED).count(),
                "cancelled": qs.filter(status=Receipt.Status.CANCELLED).count(),
                "line_count": lines.count(),
                "received_qty": float(
                    lines.aggregate(total=Sum("received_quantity"))["total"] or 0
                ),
                "pending_putaway": PutawayTask.objects.filter(
                    organization_id=request.organization.id,
                    status=PutawayTask.Status.PENDING,
                ).count(),
                "by_status": [
                    {"status": s, "count": qs.filter(status=s).count()}
                    for s in Receipt.Status.values
                ],
            }
        )

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        receipt = self.get_object()
        if receipt.status != Receipt.Status.CANCELLED:
            return Response({"detail": "Cancelled receipts cannot be started."}, status=400)
        receipt.status = Receipt.Status.IN_PROGRESS
        receipt.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(receipt).data

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        receipt = self.get_object()
        if receipt.status == Receipt.Status.CANCELLED:
            return Response({"detail": "Cancelled receipts cannot be completed."}, status=400)
        receipt.status = Receipt.Status.RECEIVED
        receipt.received_at = timezone.now()
        receipt.save(update_fields=["status", "received_at", "updated_at"])
        receipt.lines.update(received_quantity=F("quantity"))
        return Response(self.get_serializer(receipt).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        receipt = self.get_object()
        if receipt.status == Receipt.Status.RECEIVED:
            return Response({"detail": "Received receipts cannot be cancelled."}, status=400)
        receipt.status = Receipt.Status.CANCELLED
        receipt.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(receipt).data)


class ReceiptLineViewSet(TenantViewSet):
    queryset = ReceiptLine.objects.select_related("receipt", "product")
    serializer_class = ReceiptLineSerializer
    required_permission = "receiving.view"
    write_permission = "receiving.manage"
    search_fields = ["receipt__number", "product__sku", "batch_number"]
    filterset_fields = ["receipt", "product"]

    @action(detail=True, methods=["post"])
    def receive(self, request, pk=None):
        line = self.get_object()
        qty = Decimal(str(request.data.get("quantity") or line.quantity))
        line.received_quantity = qty
        line.save(update_fields=["received_quantity", "updated_at"])
        return Response(self.get_serializer(line).data)


class PutawayTaskViewSet(TenantViewSet):
    queryset = PutawayTask.objects.select_related("receipt_line", "receipt_line__product", "bin", "assigned_to")
    serializer_class = PutawayTaskSerializer
    required_permission = "receiving.view"
    write_permission = "receiving.manage"
    search_fields = ["receipt_line__receipt__number", "receipt_line__product__sku"]
    filterset_fields = ["status", "assigned_to", "bin"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = PutawayTask.Status.COMPLETED
        task.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(task).data)
