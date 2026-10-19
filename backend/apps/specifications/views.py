from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.specifications.models import (
    SpecificationItem,
    SpecificationTemplate,
    SpecificationValue,
)
from apps.specifications.serializers import (
    SpecificationItemSerializer,
    SpecificationTemplateSerializer,
    SpecificationValueSerializer,
)


class SpecificationTemplateViewSet(TenantViewSet):
    queryset = SpecificationTemplate.objects.annotate(item_count=Count("items"))
    serializer_class = SpecificationTemplateSerializer
    required_permission = "specifications.view"
    write_permission = "specifications.manage"
    search_fields = ["name", "category"]
    filterset_fields = ["category", "is_active"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        templates = self.get_queryset()
        items = SpecificationItem.objects.filter(organization=request.organization)
        values = SpecificationValue.objects.filter(organization=request.organization)
        return Response(
            {
                "template_count": templates.count(),
                "active_templates": templates.filter(is_active=True).count(),
                "item_count": items.count(),
                "required_items": items.filter(required=True).count(),
                "value_count": values.count(),
                "items_by_field_type": {
                    f: items.filter(field_type=f).count() for f, _ in SpecificationItem.FieldType.choices
                },
            }
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        template = self.get_object()
        template.is_active = False
        template.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(template).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        template = self.get_object()
        template.is_active = True
        template.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(template).data)


class SpecificationItemViewSet(TenantViewSet):
    queryset = SpecificationItem.objects.select_related("template")
    serializer_class = SpecificationItemSerializer
    required_permission = "specifications.view"
    write_permission = "specifications.manage"
    search_fields = ["name", "template__name"]
    filterset_fields = ["template", "field_type", "required"]


class SpecificationValueViewSet(TenantViewSet):
    queryset = SpecificationValue.objects.select_related("template", "item", "product")
    serializer_class = SpecificationValueSerializer
    required_permission = "specifications.view"
    write_permission = "specifications.manage"
    search_fields = ["value", "item__name", "product__sku", "template__name"]
    filterset_fields = ["template", "item", "product"]
