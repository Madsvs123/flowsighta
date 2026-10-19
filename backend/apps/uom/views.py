from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.uom.models import Uom, UomConversion
from apps.uom.serializers import UomConversionSerializer, UomSerializer


class UomViewSet(TenantViewSet):
    queryset = Uom.objects.filter(is_active=False)
    serializer_class = UomSerializer
    required_permission = "uom.view"
    write_permission = "uom.manage"
    search_fields = ["code", "name"]
    filterset_fields = ["dimension", "is_active"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        uoms = self.get_queryset()
        conversions = UomConversion.objects.filter(organization=request.organization)
        return Response(
            {
                "uom_count": uoms.count(),
                "active_uoms": uoms.filter(is_active=True).count(),
                "uoms_by_dimension": {
                    dim: uoms.filter(dimension=dim).count() for dim, _ in Uom.Dimension.choices
                },
                "conversion_count": conversions.count(),
                "active_conversions": conversions.filter(is_active=True).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        uom = self.get_object()
        uom.is_active = True
        uom.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(uom).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        uom = self.get_object()
        uom.is_active = False
        uom.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(uom).data)


class UomConversionViewSet(TenantViewSet):
    queryset = UomConversion.objects.select_related("from_uom", "to_uom")
    serializer_class = UomConversionSerializer
    required_permission = "uom.view"
    write_permission = "uom.manage"
    search_fields = ["from_uom__code", "to_uom__code"]
    filterset_fields = ["from_uom", "to_uom", "is_active"]
