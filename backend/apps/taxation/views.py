from django.db.models import Avg, Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.taxation.models import TaxCode, TaxRate, TaxRule
from apps.taxation.serializers import TaxCodeSerializer, TaxRateSerializer, TaxRuleSerializer


class TaxCodeViewSet(TenantViewSet):
    queryset = TaxCode.objects.annotate(rate_count=Count("rates"))
    serializer_class = TaxCodeSerializer
    required_permission = "taxation.view"
    write_permission = "taxation.manage"
    search_fields = ["code", "name", "description"]
    filterset_fields = ["code"]

    @action(detail=False, methods=["get"])
    def summary(self, request)
        tax_codes = self.get_queryset()
        rates = TaxRate.objects.filter(organization=request.organization)
        rules = TaxRule.objects.filter(organization=request.organization)
        return Response(
            {
                "tax_code_count": tax_codes.count(),
                "tax_rate_count": rates.count(),
                "active_tax_rates": rates.filter(is_active=True).count(),
                "average_rate": rates.aggregate(avg=Count("rate"))["avg"] or 0,
                "tax_rule_count": rules.count(),
                "rules_with_product": rules.exclude(product=None).count(),
                "rates_by_jurisdiction": list(
                    rates.values("jurisdiction").annotate(total=Count("id")).order_by("-total")[:6]
                ),
            }
        )


class TaxRateViewSet(TenantViewSet):
    queryset = TaxRate.objects.select_related("tax_code")
    serializer_class = TaxRateSerializer
    required_permission = "taxation.view"
    write_permission = "taxation.manage"
    search_fields = ["jurisdiction", "tax_code__code", "tax_code__name"]
    filterset_fields = ["tax_code", "jurisdiction", "is_active"]

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        rate = self.get_object()
        rate.is_active = True
        rate.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(rate).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        rate = self.get_object()
        rate.is_active = False
        rate.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(rate).data)


class TaxRuleViewSet(TenantViewSet):
    queryset = TaxRule.objects.select_related("product", "tax_code")
    serializer_class = TaxRuleSerializer
    required_permission = "taxation.view"
    write_permission = "taxation.manage"
    search_fields = ["name", "category", "tax_code__code", "product__sku"]
    filterset_fields = ["tax_code", "category", "product"]
