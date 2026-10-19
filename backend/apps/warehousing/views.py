from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.warehousing.models import Bin, PutawayRule, StorageZone
from apps.warehousing.serializers import BinSerializer, PutawayRuleSerializer, StorageZoneSerializer


class StorageZoneViewSet(TenantViewSet):
    queryset = StorageZone.objects.select_related("warehouse")
    serializer_class = StorageZoneSerializer
    required_permission = "warehousing.view"
    write_permission = "warehousing.manage"
    search_fields = ["code", "name", "warehouse__name"]
    filterset_fields = ["warehouse", "type"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        bins = Bin.objects.filter(zone__organization_id=request.organization.id)
        zones_by_type = []
        for zone_type in StorageZone.Type.values:
            zones_by_type.append(
                {"type": zone_type, "count": qs.filter(type=zone_type).count()}
            )
        return Response(
            {
                "zone_count": qs.count(),
                "bin_count": bins.count(),
                "active_bins": bins.filter(is_active=True).count(),
                "putaway_rules": PutawayRule.objects.filter(
                    organization_id=request.organization.id
                ).count(),
                "zones_by_type": zones_by_type,
            }
        )


class BinViewSet(TenantViewSet):
    queryset = Bin.objects.select_related("zone", "zone__warehouse")
    serializer_class = BinSerializer
    required_permission = "warehousing.view"
    write_permission = "warehousing.manage"
    search_fields = ["code", "zone__code"]
    filterset_fields = ["zone", "is_active"]

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        bin_obj = self.get_object()
        bin_obj.is_active = not bin_obj.is_active
        bin_obj.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(bin_obj).data)


class PutawayRuleViewSet(TenantViewSet):
    queryset = PutawayRule.objects.select_related("zone")
    serializer_class = PutawayRuleSerializer
    required_permission = "warehousing.view"
    write_permission = "warehousing.manage"
    search_fields = ["name", "category"]
    filterset_fields = ["zone", "category"]
