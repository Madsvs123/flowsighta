from django.db.models import Avg
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.freight.models import AccessorialCharge, FreightBill, FreightBooking, FreightQuote
from apps.freight.serializers import (
    AccessorialChargeSerializer,
    FreightBillSerializer,
    FreightBookingSerializer,
    FreightQuoteSerializer,
)


class FreightQuoteViewSet(TenantViewSet):
    queryset = FreightQuote.objects.select_related("carrier")
    serializer_class = FreightQuoteSerializer
    required_permission = "freight.view"
    write_permission = "freight.manage"
    search_fields = ["origin", "destination", "carrier__name", "carrier__code"]
    filterset_fields = ["mode", "status", "carrier"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        return Response(
            {
                "quote_count": qs.count(),
                "active_quotes": qs.filter(status=FreightQuote.Status.ACTIVE).count(),
                "expired_quotes": qs.filter(status=FreightQuote.Status.EXPIRED).count(),
                "by_mode": {mode: qs.filter(mode=mode).count() for mode, _ in FreightQuote.Mode.choices},
                "avg_rate": float(qs.aggregate(avg=Avg("rate"))["avg"] or 0),
            }
        )


class FreightBookingViewSet(TenantViewSet):
    queryset = FreightBooking.objects.select_related("quote", "quote__carrier")
    serializer_class = FreightBookingSerializer
    required_permission = "freight.view"
    write_permission = "freight.manage"
    search_fields = ["reference", "quote__origin", "quote__destination"]
    filterset_fields = ["status", "quote"]

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        if booking.status == FreightBooking.Status.CANCELLED:
            return Response({"detail": "Cancelled bookings cannot be confirmed."}, status=400)
        booking.status = FreightBooking.Status.CONFIRMED
        booking.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=["post"])
    def book(self, request, pk=None):
        booking = self.get_object()
        if booking.status == FreightBooking.Status.CANCELLED:
            return Response({"detail": "Cancelled bookings cannot be booked."}, status=400)
        booking.status = FreightBooking.Status.CONFIRMED
        booking.booked_at = timezone.now()
        booking.save(update_fields=["status", "booked_at", "updated_at"])
        return Response(self.get_serializer(booking).data)


class FreightBillViewSet(TenantViewSet):
    queryset = FreightBill.objects.select_related("booking", "booking__quote")
    serializer_class = FreightBillSerializer
    required_permission = "freight.view"
    write_permission = "freight.manage"
    search_fields = ["number", "booking__reference"]
    filterset_fields = ["status", "booking"]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        bill = self.get_object()
        if bill.status == FreightBill.Status.APPROVED:
            return Response({"detail": "Paid bills cannot be re-approved."}, status=400)
        bill.status = FreightBill.Status.APPROVED
        bill.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(bill).data)

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        bill = self.get_object()
        bill.status = FreightBill.Status.PAID
        bill.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(bill).data)


class AccessorialChargeViewSet(TenantViewSet):
    queryset = AccessorialCharge.objects.select_related("booking")
    serializer_class = AccessorialChargeSerializer
    required_permission = "freight.view"
    write_permission = "freight.manage"
    search_fields = ["type", "description", "booking__reference"]
    filterset_fields = ["booking", "type"]
