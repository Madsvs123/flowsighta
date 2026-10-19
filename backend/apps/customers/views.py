from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.customers.models import Customer, CustomerAddress, CustomerAgreement, CustomerContact
from apps.customers.serializers import (
    CustomerAddressSerializer,
    CustomerAgreementSerializer,
    CustomerContactSerializer,
    CustomerSerializer,
)


class CustomerViewSet(TenantViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    required_permission = "customers.view"
    write_permission = "customers.manage"
    search_fields = ["code", "name", "country", "payment_terms"]
    filterset_fields = ["status", "country", "is_tax_exempt"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        credit = qs.aggregate(total_credit_limit=Sum("credit_limit"))
        return Response(
            {
                "customers": qs.count(),
                "active": qs.filter(status=Customer.Status.ACTIVE).count(),
                "inactive": qs.filter(status=Customer.Status.INACTIVE).count(),
                "blacklisted": qs.filter(status=Customer.Status.BLACKLISTED).count(),
                "tax_exempt": qs.filter(is_tax_exempt=True).count(),
                "total_credit_limit": float(credit["total_credit_limit"] or 0),
            }
        )

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        customer = self.get_object()
        status = request.data.get("status")
        if status not in Customer.Status.values:
        return Response({"detail": f"Invalid status: {status}"}, status=400)
        customer.status = status
        customer.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(customer).data)


class CustomerContactViewSet(TenantViewSet):
    queryset = CustomerContact.objects.select_related("customer")
    serializer_class = CustomerContactSerializer
    required_permission = "customers.view"
    write_permission = "customers.manage"
    search_fields = ["name", "email", "phone", "customer__name"]
    filterset_fields = ["customer", "role"]


class CustomerAddressViewSet(TenantViewSet):
    queryset = CustomerAddress.objects.select_related("customer")
    serializer_class = CustomerAddressSerializer
    required_permission = "customers.view"
    write_permission = "customers.manage"
    search_fields = ["address", "customer__name"]
    filterset_fields = ["customer", "type", "is_default"]


class CustomerAgreementViewSet(TenantViewSet):
    queryset = CustomerAgreement.objects.select_related("customer")
    serializer_class = CustomerAgreementSerializer
    required_permission = "customers.view"
    write_permission = "customers.manage"
    search_fields = ["title", "customer__name"]
    filterset_fields = ["customer", "status"]
