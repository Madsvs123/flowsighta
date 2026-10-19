from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.subscriptions.models import Renewal, Subscription, SubscriptionInvoice, SubscriptionLine


class SubscriptionSerializer(TenantSerializer):
    class Meta:
        model = Subscription
        fields = (
            "id",
            "customer_ref",
            "plan",
            "status",
            "billing_cycle",
            "price",
            "start_date",
            "next_billing_date",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SubscriptionLineSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    plan = serializers.CharField(source="subscription.plan", read_only=True)

    class Meta:
        model = SubscriptionLine
        fields = (
            "id",
            "subscription",
            "plan",
            "product",
            "sku",
            "product_name",
            "quantity",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SubscriptionInvoiceSerializer(TenantSerializer):
    plan = serializers.CharField(source="subscription.plan", read_only=True)
    customer_ref = serializers.CharField(source="subscription.customer_ref", read_only=True)

    class Meta:
        model = SubscriptionInvoice
        fields = (
            "id",
            "subscription",
            "plan",
            "customer_ref",
            "period_start",
            "period_end",
            "amount",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class RenewalSerializer(TenantSerializer):
    plan = serializers.CharField(source="subscription.plan", read_only=True)
    customer_ref = serializers.CharField(source="subscription.customer_ref", read_only=True)

    class Meta:
        model = Renewal
        fields = (
            "id",
            "subscription",
            "plan",
            "customer_ref",
            "renewal_date",
            "status",
            "amount",
            "created_at",
        )
         read_only_fields = ("id", "created_at")
