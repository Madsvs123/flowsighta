from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.quotes.models import QuoteConversion, QuoteLine, QuoteRevision, SalesQuote
from apps.quotes.serializers import (
    QuoteConversionSerializer,
    QuoteLineSerializer,
    QuoteRevisionSerializer,
    SalesQuoteSerializer,
)


class SalesQuoteViewSet(TenantViewSet):
    queryset = SalesQuote.objects.all()
    serializer_class = SalesQuoteSerializer
    required_permission = "quotes.view"
    write_permission = "quotes.manage"
    search_fields = ["number", "customer_ref"]
    filterset_fields = ["status", "currency", "valid_until"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        totals = qs.aggregate(subtotal=Sum("subtotal"), total=Sum("total"))
        return Response(
            {
                "quotes": qs.count(),
                "open_quotes": qs.filter(status__in=["draft", "sent"]).count(),
                "accepted": qs.filter(status=SalesQuote.Status.ACCEPTED).count(),
                "rejected": qs.filter(status=SalesQuote.Status.REJECTED).count(),
                "expired": qs.filter(status=SalesQuote.Status.EXPIRED).count(),
                "subtotal": float(totals["subtotal"] or 0),
                "total": float(totals["total"] or 0),
            }
        )

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        quote = self.get_object()
        if quote.status != SalesQuote.Status.DRAFT:
            quote.status = SalesQuote.Status.SENT
        return Response(self.get_serializer(quote).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        quote = self.get_object()
        if quote.status in (SalesQuote.Status.REJECTED, SalesQuote.Status.EXPIRED):
            return Response({"detail": f"Quotes in status {quote.status} cannot be accepted."}, status=400)
        quote.status = SalesQuote.Status.ACCEPTED
        quote.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(quote).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        quote = self.get_object()
        if quote.status in (SalesQuote.Status.ACCEPTED, SalesQuote.Status.EXPIRED):
            return Response({"detail": f"Quotes in status {quote.status} cannot be rejected."}, status=400)
        quote.status = SalesQuote.Status.REJECTED
        quote.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(quote).data)

    @action(detail=True, methods=["post"])
    def convert(self, request, pk=None):
        quote = self.get_object()
        quote.status = SalesQuote.Status.ACCEPTED
        quote.save(update_fields=["status", "updated_at"])
        conversion = QuoteConversion.objects.create(
            organization=quote.organization,
            quote=quote,
            sales_order_ref=request.data.get("sales_order_ref", ""),
        )
        return Response(QuoteConversionSerializer(conversion).data)


class QuoteLineViewSet(TenantViewSet):
    queryset = QuoteLine.objects.select_related("quote", "product")
    serializer_class = QuoteLineSerializer
    required_permission = "quotes.view"
    write_permission = "quotes.manage"
    search_fields = ["quote__number", "product__sku", "product__name"]
    filterset_fields = ["quote", "product"]


class QuoteRevisionViewSet(TenantViewSet):
    queryset = QuoteRevision.objects.select_related("quote", "revised_by")
    serializer_class = QuoteRevisionSerializer
    required_permission = "quotes.view"
    write_permission = "quotes.manage"
    search_fields = ["quote__number", "notes"]
    filterset_fields = ["quote", "version"]


class QuoteConversionViewSet(TenantViewSet):
    queryset = QuoteConversion.objects.select_related("quote")
    serializer_class = QuoteConversionSerializer
    required_permission = "quotes.view"
    write_permission = "quotes.manage"
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["quote__number", "sales_order_ref"]
    filterset_fields = ["quote"]
