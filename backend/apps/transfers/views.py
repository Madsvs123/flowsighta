from django.db.models import F, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.core.services import next_number
from apps.transfers.models import TransferLine, TransferOrder, TransferShipment
from apps.transfers.serializers import (
    TransferLineSerializer,
    TransferOrderSerializer,
    TransferShipmentSerializer,
)


class TransferOrderViewSet(TenantViewSet):
    queryset = TransferOrder.objects.select_related("from_warehouse", "to_warehouse", "requested_by")
    serializer_class = TransferOrderSerializer
    required_permission = "transfers.view"
    write_permission = "transfers.manage"
    search_fields = ["number", "from_warehouse__code", "to_warehouse__code", "notes"]
    filterset_fields = ["from_warehouse", "to_warehouse", "status"]

    def perform_create(self, serializer):
        instance = serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        if not instance.number:
            instance.number = next_number(TransferOrder, instance.organization, "TRF")
            instance.save(update_fields=["number"])

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        lines = TransferLine.objects.filter(order__organization_id=request.organization.id)
        return Response(
            {
                "order_total": qs.count(),
                "draft": qs.filter(status=TransferOrder.Status.DRAFT).count(),
                "approved": qs.filter(status=TransferOrder.Status.APPROVED).count(),
                "in_transit": qs.filter(status=TransferOrder.Status.IN_TRANSIT).count(),
                "received": qs.filter(status=TransferOrder.Status.RECEIVED).count(),
                "cancelled": qs.filter(status=TransferOrder.Status.CANCELLED).count(),
                "line_count": lines.count(),
                "qty_shipped": float(
                    lines.aggregate(total=Sum("shipped_quantity"))["total"] or 0
                ),
                "qty_received": float(
                    lines.aggregate(total=Sum("received_quantity"))["total"] or 0
                ),
                "active_shipments": TransferShipment.objects.filter(
                    organization_id=request.organization.id,
                    status=TransferShipment.Status.IN_TRANSIT,
                ).count(),
                "by_status": [
                    {"status": s, "count": qs.filter(status=s).count()}
                    for s in TransferOrder.Status.values
                ],
            }
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        order = self.get_object()
        if order.status != TransferOrder.Status.DRAFT:
            return Response({"detail": "Only draft orders can be approved."}, status=400)
        order.status = TransferOrder.Status.APPROVED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def ship(self, request, pk=None):
        order = self.get_object()
        if order.status not in (
            TransferOrder.Status.APPROVED,
            TransferOrder.Status.DRAFT,
        ):
            return Response({"detail": "Order cannot be shipped in its current state."}, status=400)
        order.status = TransferOrder.Status.IN_TRANSIT
        order.save(update_fields=["status", "updated_at"])
        order.lines.update(shipped_quantity=F("quantity"))
        shipment, _ = TransferShipment.objects.get_or_create(
            organization=order.organization,
            order=order,
            defaults={
                "status": TransferShipment.Status.IN_TRANSIT,
                "shipped_at": timezone.now(),
                "tracking_number": request.data.get("tracking_number", ""),
            },
        )
        if shipment.status != TransferShipment.Status.IN_TRANSIT:
            shipment.status = TransferShipment.Status.IN_TRANSIT
            shipment.shipped_at = timezone.now()
            shipment.save(update_fields=["status", "shipped_at", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def receive(self, request, pk=None):
        order = self.get_object()
        if order.status not in (
            TransferOrder.Status.APPROVED,
            TransferOrder.Status.DRAFT,
        ):
            return Response({"detail": "Order cannot be received in its current state."}, status=400)
        order.status = TransferOrder.Status.RECEIVED
        order.save(update_fields=["status", "updated_at"])
        order.lines.update(received_quantity=F("quantity"))
        order.shipments.filter(status=TransferShipment.Status.IN_TRANSIT).update(
            status=TransferShipment.Status.DELIVERED,
            delivered_at=timezone.now(),
        )
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status != TransferOrder.Status.RECEIVED:
            return Response({"detail": "Received orders cannot be cancelled."}, status=400)
        order.status = TransferOrder.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)


class TransferLineViewSet(TenantViewSet):
    queryset = TransferLine.objects.select_related("order", "product")
    serializer_class = TransferLineSerializer
    required_permission = "transfers.view"
    write_permission = "transfers.manage"
    search_fields = ["order__number", "product__sku"]
    filterset_fields = ["order", "product"]


class TransferShipmentViewSet(TenantViewSet):
    queryset = TransferShipment.objects.select_related("order", "carrier")
    serializer_class = TransferShipmentSerializer
    required_permission = "transfers.view"
    write_permission = "transfers.manage"
    search_fields = ["order__number", "tracking_number", "carrier__name"]
    filterset_fields = ["order", "carrier", "status"]

    @action(detail=True, methods=["post"])
    def depart(self, request, pk=None):
        shipment = self.get_object()
        if shipment.status != TransferShipment.Status.PLANNED:
            return Response({"detail": "Only planned shipments can depart."}, status=400)
        shipment.status = TransferShipment.Status.IN_TRANSIT
        shipment.shipped_at = timezone.now()
        shipment.tracking_number = request.data.get("tracking_number", shipment.tracking_number)
        shipment.save(update_fields=["status", "shipped_at", "tracking_number", "updated_at"])
        return Response(self.get_serializer(shipment).data)

    @action(detail=True, methods=["post"])
    def deliver(self, request, pk=None):
        shipment = self.get_object()
        shipment.status = TransferShipment.Status.DELIVERED
        shipment.delivered_at = timezone.now()
        shipment.save(update_fields=["status", "delivered_at", "updated_at"])
        return Response(self.get_serializer(shipment).data)
