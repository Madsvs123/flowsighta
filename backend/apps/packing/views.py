from django.db.models import Count, Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.packing.models import Box, PackedItem, PackingSession
from apps.packing.serializers import BoxSerializer, PackedItemSerializer, PackingSessionSerializer


class PackingSessionViewSet(TenantViewSet):
    queryset = PackingSession.objects.select_related("shipment", "packed_by").annotate(
        box_count=Count("boxes"),
        item_count=Count("boxes__items"),
    )
    serializer_class = PackingSessionSerializer
    required_permission = "packing.view"
    write_permission = "packing.manage"
    search_fields = ["number", "shipment__number", "packed_by__email"]
    filterset_fields = ["status", "shipment", "packed_by"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        boxes = Box.objects.filter(organization=request.organization)
        items = PackedItem.objects.filter(organization=request.organization)
        return Response(
            {
                "sessions": qs.count(),
                "open_sessions": qs.filter(status=PackingSession.Status.OPEN).count(),
                "in_progress": qs.filter(status=PackingSession.Status.OPEN).count(),
                "closed_sessions": qs.filter(status=PackingSession.Status.CLOSED).count(),
                "boxes": boxes.count(),
                "sealed_boxes": boxes.filter(is_sealed=True).count(),
                "items_packed": float(items.aggregate(total=Sum("quantity")["total"] or 0),
                "total_weight": float(boxes.aggregate(total=Sum("weight"))["total"] or 0),
            }
        )

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        session = self.get_object()
        session.status = PackingSession.Status.CLOSED
        session.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(session).data)


class BoxViewSet(TenantViewSet):
    queryset = Box.objects.select_related("session").annotate(item_count=Count("items"))
    serializer_class = BoxSerializer
    required_permission = "packing.view"
    write_permission = "packing.manage"
    search_fields = ["code", "session__number"]
    filterset_fields = ["session", "is_sealed"]

    @action(detail=True, methods=["post"])
    def seal(self, request, pk=None):
        box = self.get_object()
        box.is_sealed = True
        box.save(update_fields=["is_sealed", "updated_at"])
        return Response(self.get_serializer(box).data)


class PackedItemViewSet(TenantViewSet):
    queryset = PackedItem.objects.select_related("box", "product")
    serializer_class = PackedItemSerializer
    required_permission = "packing.view"
    write_permission = "packing.manage"
    search_fields = ["product__sku", "batch_number", "box__code"]
    filterset_fields = ["box", "product"]
