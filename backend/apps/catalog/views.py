from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.catalog.models import Attribute, AttributeValue, Category, ProductVariant
from apps.catalog.serializers import (
    AttributeSerializer,
    AttributeValueSerializer,
    CategorySerializer,
    ProductVariantSerializer,
)
from apps.core.mixins import TenantViewSet


class CategoryViewSet(TenantViewSet):
    queryset = Category.objects.select_related("parent")
    serializer_class = CategorySerializer
    required_permission = "catalog.view"
    write_permission = "catalog.manage"
    search_fields = ["name"]
    filterset_fields = ["is_active", "parent"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        categories = self.get_queryset()
        attributes = Attribute.objects.filter(organization=request.organization)
        variants = ProductVariant.objects.filter(organization=request.organization)
        top = list(
            categories.annotate(children_count=Count("children"))
            .order_by("children_count")[:5]
            .values("name", "children_count", "is_active")
        )
        return Response(
            {
                "category_count": categories.count(),
                "active_categories": categories.filter(is_active=True).count(),
                "attribute_count": attributes.count(),
                "attribute_value_count": AttributeValue.objects.filter(
                    organization=request.organization
                ).count(),
                "variant_count": variants.count(),
                "active_variants": variants.filter(is_active=True).count(),
                "attributes_by_type": {
                    t: attributes.filter(type=t).count() for t, _ in Attribute.Type.choices
                },
                "top_categories": top,
            }
        )


class AttributeViewSet(TenantViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    required_permission = "catalog.view"
    write_permission = "catalog.manage"
    search_fields = ["name"]
    filterset_fields = ["type"]


class AttributeValueViewSet(TenantViewSet):
    queryset = AttributeValue.objects.select_related("attribute", "product")
    serializer_class = AttributeValueSerializer
    required_permission = "catalog.view"
    write_permission = "catalog.manage"
    search_fields = ["value", "attribute__name", "product__sku"]
    filterset_fields = ["attribute", "product"]


class ProductVariantViewSet(TenantViewSet):
    queryset = ProductVariant.objects.select_related("product")
    serializer_class = ProductVariantSerializer
    required_permission = "catalog.view"
    write_permission = "catalog.manage"
    search_fields = ["sku", "product__sku", "product__name"]
    filterset_fields = ["product", "is_active"]

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        variant = self.get_object()
        variant.is_active = True
        variant.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(variant).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        variant = self.get_object()
        variant.is_active = False
        variant.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(variant).data)
