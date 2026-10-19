from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.customers.models import Customer, CustomerAddress, CustomerAgreement, CustomerContact


class CustomerSerializer(TenantSerializer):
    class Meta:
        model = Customer
        fields = (
            "id",
            "code",
            "name",
            "status",
            "country",
            "credit_limit",
            "payment_terms",
            "is_tax_exempt",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CustomerContactSerializer(TenantSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = CustomerContact
        fields = ("id", "customer", "customer_name", "name", "email", "phone_number", "role", "created_at")
        read_only_fields = ("id", "created_at")


class CustomerAddressSerializer(TenantSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = CustomerAddress
        fields = ("id", "customer", "customer_name", "type", "address", "is_default", "created_at")
        read_only_fields = ("id", "created_at")


class CustomerAgreementSerializer(TenantSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = CustomerAgreement
        fields = (
            "id",
            "customer",
            "customer_name",
            "title",
            "start_date",
            "end_date",
            "discount_pct",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
