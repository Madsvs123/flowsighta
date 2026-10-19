from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.pricing.models import Discount, PriceChange, PriceList, PriceListItem
from apps.pricing.serializers import (
    DiscountSerializer,
    PriceChangeSerializer,
    PriceListSerializer,
    PriceListItemSerializer,
)


class PriceListViewSet(TenantViewSet):
    queryset = PriceList.objects.annotate(item_count=Count("items"))
    serializer_class = PriceListSerializer
    required_permission = "pricing.view"
    write_permission = "pricing.manage"
    search_fields = ["name", "currency"]
    filterset_fields = ["status", "is_default", "currency"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        price_lists = self.get_queryset()
        items = PriceListItem.objects.filter(organization=request.organization)
        discounts = Discount.objects.filter(organization=request.organization)
        changes = PriceChange.objects.filter(organization=request.organization)
        return Response(
            {
                "price_list_count": price_lists.count(),
                "active_price_lists": price_lists.filter(status=PriceList.Status.ACTIVE).count(),
                "default_price_list": price_lists.filter(is_default=True).first().name
                if price_lists.filter(is_default=True).exists()
                else None,
                "price_list_item_count": items.count(),
                "discount_count": discounts.count(),
                "active_discounts": discounts.filter(status=Discount.Status.ACTIVE).count(),
                "price_change_count": changes.count(),
                "items_by_list": list(
                    items.values("price_list__name").annotate(total=Count("id")).order_by("total")[:5]
                ),
            }
        )


class PriceListItemViewSet(TenantViewSet):
    queryset = PriceListItem.objects.select_related("price_list", "product")
    serializer_class = PriceListItemSerializer
    required_permission = "pricing.view"
    write_permission = "pricing.manage"
    search_fields = ["product__sku", "product__name", "price_list__name"]
    filterset_fields = ["price_list", "product"]


class DiscountViewSet(TenantViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    required_permission = "pricing.view"
    write_permission = "pricing.manage"
    search_fields = ["name"]
    filterset_fields = ["type", "status"]

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        discount = self.get_object()
        discount.status = Discount.Status.ACTIVE
        discount.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(discount).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        discount = self.get_object()
        discount.status = Discount.Status.INACTIVE
        discount.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(discount).data)


class PriceChangeViewSet(TenantViewSet):
    queryset = PriceChange.objects.select_related("product", "changed_by")
    serializer_class = PriceChangeSerializer
    required_permission = "pricing.view"
    write_permission = "pricing.manage"
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["product__sku", "product__name", "reason"]
    filterset_fields = ["product"]
