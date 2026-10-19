from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.yard.models import YardGateLog, YardLocation, YardMove
from apps.yard.serializers import YardGateLogSerializer, YardLocationSerializer, YardMoveSerializer


class YardLocationViewSet(TenantViewSet):
    queryset = YardLocation.objects.select_related("warehouse").annotate(move_count=Count("moves"))
    serializer_class = YardLocationSerializer
    required_permission = "yard.view"
    write_permission = "yard.manage"
    search_fields = ["code", "warehouse__name", "warehouse__code"]
    filterset_fields = ["warehouse", "type", "is_active"]


class YardMoveViewSet(TenantViewSet):
    queryset = YardMove.objects.select_related("location", "location__warehouse")
    serializer_class = YardMoveSerializer
    required_permission = "yard.view"
    write_permission = "yard.manage"
    search_fields = ["vehicle", "trailer", "location__code"]
    filterset_fields = ["location", "status", "direction"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        logs = YardGateLog.objects.filter(organization=request.organization)
        locations = YardLocation.objects.filter(organization=request.organization, is_active=True)
        return Response(
            {
                "moves": qs.count(),
                "requested": qs.filter(status=YardMove.Status.REQUESTED).count(),
                "moving": qs.filter(status=YardMove.Status.MOVING).count(),
                "parked": qs.filter(status=YardMove.Status.PARKED).count(),
                "departed": qs.filter(status=YardMove.Status.DEPARTED).count(),
                "occupied_locations": qs.filter(
                    status__in=[YardMove.Status.REQUESTED, YardMove.Status.MOVING, YardMove.Status.PARKED]
                )
                .values("location")
                .distinct()
                .count(),
                "locations": locations.count(),
                "gate_ins": logs.filter(direction=YardGateLog.Direction.IN).count(),
                "gate_outs": logs.filter(direction=YardGateLog.Direction.OUT).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def park(self, request, pk=None):
        move = self.get_object()
        move.status = YardMove.Status.PARKED
        move.moved_at = timezone.now()
        move.save(update_fields=["status", "moved_at", "updated_at"])
        return Response(self.get_serializer(move).data)

    @action(detail=True, methods=["post"])
    def depart(self, request, pk=None):
        move = self.get_object()
        move.status = YardMove.Status.DEPARTED
        move.moved_at = timezone.now()
        move.save(update_fields=["status", "moved_at", "updated_at"])
        return Response(self.get_serializer(move).data)


class YardGateLogViewSet(TenantViewSet):
    queryset = YardGateLog.objects.all()
    serializer_class = YardGateLogSerializer
    required_permission = "yard.view"
    write_permission = "yard.manage"
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["vehicle", "trailer", "driver", "gate"]
    filterset_fields = ["direction", "gate"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            occurred_at=serializer.validated_data.get("occurred_at") and timezone.now(),
        )
