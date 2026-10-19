from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.sales_orders.models import OrderAllocation, SalesOrder, SalesOrderLine, SalesShipment
from apps.sales_orders.serializers import (
    OrderAllocationSerializer,
    SalesOrderLineSerializer,
    SalesOrderSerializer,
    SalesShipmentSerializer,
)


class SalesOrderViewSet(TenantViewSet):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    required_permission = "sales_orders.view"
    write_permission = "sales_orders.manage"
    search_fields = ["number", "customer_ref", "notes"]
    filterset_fields = ["status", "currency", "order_date", "requested_date"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        totals = qs.aggregate(subtotal=Sum("subtotal"), tax_total=Sum("tax_total"), total=Count("total"))
        return Response(
            {
                "orders": qs.count(),
                "open_orders": qs.filter(status__in=["draft", "confirmed", "allocated", "picked"]).count(),
                "shipped": qs.filter(status__in=["shipped", "delivered"]).count(),
                "cancelled": qs.filter(status="cancelled").count(),
                "subtotal": float(totals["subtotal"] or 0),
                "tax_total": float(totals["tax_total"] or 0),
                "total": float(totals["total"] or 0),
            }
        )

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        order = self.get_object()
        if order.status == SalesOrder.Status.CANCELLED:
        return Response({"detail": "Cancelled orders cannot be confirmed."}, status=400)
        if order.status == SalesOrder.Status.DRAFT:
            order.status = SalesOrder.Status.CONFIRMED
            order.order_date = order.order_date or timezone.now().date()
            order.save(update_fields=["status", "order_date", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in (SalesOrder.Status.DELIVERED, SalesOrder.Status.CANCELLED):
            return Response({"detail": f"Orders in status {order.status} cannot be cancelled."}, status=400)
        order.status = SalesOrder.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)


class SalesOrderLineViewSet(TenantViewSet):
    queryset = SalesOrderLine.objects.select_related("order", "product")
    serializer_class = SalesOrderLineSerializer
    required_permission = "sales_orders.view"
    write_permission = "sales_orders.manage"
    search_fields = ["order__number", "product__sku", "product__name"]
    filterset_fields = ["order", "product"]


class OrderAllocationViewSet(TenantViewSet):
    queryset = OrderAllocation.objects.select_related("line__order", "stock_item__product")
    serializer_class = OrderAllocationSerializer
    required_permission = "sales_orders.view"
    write_permission = "sales_orders.manage"
    search_fields = ["line__order__number", "stock_item__product__sku"]
    filterset_fields = ["line", "stock_item"]


class SalesShipmentViewSet(TenantViewSet):
    queryset = SalesShipment.objects.select_related("order")
    serializer_class = SalesShipmentSerializer
    required_permission = "sales_orders.view"
    write_permission = "sales_orders.manage"
    search_fields = ["order__number", "tracking_number"]
    filterset_fields = ["order", "status"]

    @action(detail=True, methods=["post"])
    def ship(self, request, pk=None):
        shipment = self.get_object()
        shipment.status = SalesShipment.Status.SHIPPED
        shipment.shipped_at = timezone.now()
        shipment.tracking_number = request.data.get("tracking_number", shipment.tracking_number)
        shipment.save(update_fields=["status", "shipped_at", "tracking_number", "updated_at"])
        order = shipment.order
        order.status = SalesOrder.Status.SHIPPED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(shipment).data)
