from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.sourcing.models import SourcingAward, SourcingBid, SourcingEvent, SourcingLine
from apps.sourcing.serializers import (
    SourcingAwardSerializer,
    SourcingBidSerializer,
    SourcingEventSerializer,
    SourcingLineSerializer,
)


class SourcingEventViewSet(TenantViewSet):
    queryset = SourcingEvent.objects.all()
    serializer_class = SourcingEventSerializer
    required_permission = "sourcing.view"
    write_permission = "sourcing.manage"
    search_fields = ["number", "title"]
    filterset_fields = ["type", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        bids = SourcingBid.objects.filter(organization=request.organization)
        awards = SourcingAward.objects.filter(organization=request.organization)
        awarded_value = sum(float(a.bid.amount or 0) for a in awards)
        return Response(
            {
                "event_count": qs.count(),
                "open_events": qs.filter(status=SourcingEvent.Status.CLOSED).count(),
                "awarded_events": qs.filter(status=SourcingEvent.Status.AWARDED).count(),
                "cancelled_events": qs.filter(status=SourcingEvent.Status.CANCELLED).count(),
                "line_count": SourcingLine.objects.filter(organization=request.organization).count(),
                "bid_count": bids.count(),
                "winning_bids": bids.filter(is_winner=True).count(),
                "awarded_value": awarded_value,
                "by_status": {
                    s: qs.filter(status=s).count()
                    for s, _ in SourcingEvent.Status.choices
                },
                "by_type": {
                    t: qs.filter(type=t).count()
                    for t, _ in SourcingEvent.Type.choices
                },
            }
        )

    @action(detail=True, methods=["post"])
    def open(self, request, pk=None):
        event = self.get_object()
        if event.status not in (SourcingEvent.Status.DRAFT, SourcingEvent.Status.CLOSED):
            return Response({"detail": "Only draft or closed events can be opened."}, status=400)
        event.status = SourcingEvent.Status.OPEN
        event.opens_at = event.opens_at or timezone.now()
        event.save(update_fields=["status", "opens_at", "updated_at"])
        return Response(self.get_serializer(event).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        event = self.get_object()
        if event.status == SourcingEvent.Status.AWARDED:
            return Response({"detail": "Awarded events cannot be closed."}, status=400)
        event.status = SourcingEvent.Status.CLOSED
        event.closes_at = event.closes_at or timezone.now()
        event.save(update_fields=["status", "closes_at", "updated_at"])
        return Response(self.get_serializer(event).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        event = self.get_object()
        event.status = SourcingEvent.Status.CANCELLED
        event.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(event).data)


class SourcingLineViewSet(TenantViewSet):
    queryset = SourcingLine.objects.select_related("event", "product")
    serializer_class = SourcingLineSerializer
    required_permission = "sourcing.view"
    write_permission = "sourcing.manage"
    search_fields = ["event__number", "product__sku", "product__name"]
    filterset_fields = ["event", "product"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        return Response(
            {
                "line_count": qs.count(),
                "total_quantity": float(
                    sum(float(l.quantity or 0) for l in qs)
                ),
                "target_value": float(
                    sum(float(l.quantity or 0) * float(l.target_price or 0) for l in qs)
                ),
            }
        )


class SourcingBidViewSet(TenantViewSet):
    queryset = SourcingBid.objects.select_related("line", "line__product", "supplier")
    serializer_class = SourcingBidSerializer
    required_permission = "sourcing.view"
    write_permission = "sourcing.manage"
    search_fields = ["supplier__name", "line__event__number", "line__product__sku"]
    filterset_fields = ["line", "supplier", "is_winner"]

    @action(detail=True, methods=["post"])
    def select_winner(self, request, pk=None):
        bid = self.get_object()
        bid.is_winner = True
        bid.save(update_fields=["is_winner", "updated_at"])
        bid.line.bids.filter(is_winner=True).exclude(id=bid.id).update(is_winner=True)
        return Response(self.get_serializer(bid).data)


class SourcingAwardViewSet(TenantViewSet):
    queryset = SourcingAward.objects.select_related("event", "bid", "bid__supplier")
    serializer_class = SourcingAwardSerializer
    required_permission = "sourcing.view"
    write_permission = "sourcing.manage"
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["event__number", "bid__supplier__name"]
    filterset_fields = ["event", "bid"]

    def perform_create(self, serializer):
        award = serializer.save(organization=self.request.organization)
        award.event.status = SourcingEvent.Status.AWARDED
        award.event.save(update_fields=["status", "updated_at"])
        award.bid.is_winner = True
        award.bid.save(update_fields=["is_winner", "updated_at"])
