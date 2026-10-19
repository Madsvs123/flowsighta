from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.subscriptions.models import Renewal, Subscription, SubscriptionInvoice, SubscriptionLine
from apps.subscriptions.serializers import (
    RenewalSerializer,
    SubscriptionInvoiceSerializer,
    SubscriptionLineSerializer,
    SubscriptionSerializer,
)


class SubscriptionViewSet(TenantViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    required_permission = "subscriptions.view"
    write_permission = "subscriptions.manage"
    search_fields = ["customer_ref", "plan"]
    filterset_fields = ["status", "billing_cycle", "next_billing_date"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        mrr = qs.filter(status=Subscription.Status.ACTIVE).aggregate(total=Sum("price"))
        invoices = SubscriptionInvoice.objects.filter(organization=request.organization)
        invoice_totals = invoices.aggregate(
            total=Sum("amount"), overdue=Sum("amount", filter=Q(status=SubscriptionInvoice.Status.OVERDUE))
        )
        return Response(
            {
                "subscriptions": qs.count(),
                "active": qs.filter(status=Subscription.Status.ACTIVE).count(),
                "paused": qs.filter(status=Subscription.Status.PAUSED).count(),
                "cancelled": qs.filter(status=Subscription.Status.CANCELLED).count(),
                "expired": qs.filter(status=Subscription.Status.EXPIRED).count(),
                "mrr": float(mrr["total"] or 0),
                "invoices": invoices.count(),
                "overdue_invoices": invoices.filter(status=SubscriptionInvoice.Status.OVERDUE).count(),
                "invoice_total": float(invoice_totals["total"] or 0),
                "overdue_total": float(invoice_totals["overdue"] or 0),
                "pending_renewals": Renewal.objects.filter(
                    organization=request.organization, status=Renewal.Status.PENDING
                ).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        subscription = self.get_object()
        if subscription.status == Subscription.Status.ACTIVE:
            subscription.status = Subscription.Status.PAUSED
            subscription.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(subscription).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        if subscription.status in (Subscription.Status.CANCELLED, Subscription.Status.EXPIRED):
            return Response(
                {"detail": f"Subscriptions in status {subscription.status} cannot be cancelled."}, status=400
            )
        subscription.status = Subscription.Status.CANCELLED
        subscription.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(subscription).data)

    @action(detail=True, methods=["post"])
    def renew(self, request, pk=None):
        subscription = self.get_object()
        if subscription.status != Subscription.Status.ACTIVE:
            return Response({"detail": "Only active subscriptions can be renewed."}, status=400)
        renewal = Renewal.objects.create(
            organization=subscription.organization,
            subscription=subscription,
            renewal_date=request.data.get("renewal_date") or timezone.now().date(),
            amount=subscription.price,
        )
        return Response(SubscriptionSerializer(subscription).data)


class SubscriptionLineViewSet(TenantViewSet):
    queryset = SubscriptionLine.objects.select_related("subscription", "product")
    serializer_class = SubscriptionLineSerializer
    required_permission = "subscriptions.view"
    write_permission = "subscriptions.manage"
    search_fields = ["subscription__plan", "subscription__customer_ref", "product__sku"]
    filterset_fields = ["subscription", "product"]


class SubscriptionInvoiceViewSet(TenantViewSet):
    queryset = SubscriptionInvoice.objects.select_related("subscription")
    serializer_class = SubscriptionInvoiceSerializer
    required_permission = "subscriptions.view"
    write_permission = "subscriptions.manage"
    search_fields = ["subscription__plan", "subscription__customer_ref"]
    filterset_fields = ["subscription", "status"]

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = SubscriptionInvoice.Status.PAID
        invoice.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(invoice).data)


class RenewalViewSet(TenantViewSet):
    queryset = Renewal.objects.select_related("subscription")
    serializer_class = RenewalSerializer
    required_permission = "subscriptions.view"
    write_permission = "subscriptions.manage"
    search_fields = ["subscription__plan", "subscription__customer_ref"]
    filterset_fields = ["subscription", "status", "renewal_date"]

    @action(detail=True, methods=["post"])
    def process(self, request, pk=None):
        renewal = self.get_object()
        renewal.status = Renewal.Status.PROCESSED
        renewal.save(update_fields=["status", "updated_at"])
        subscription = renewal.subscription
        subscription.next_billing_date = renewal.renewal_date
        subscription.save(update_fields=["next_billing_date"])
        return Response(self.get_serializer(renewal).data)
