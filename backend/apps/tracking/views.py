from datetime import timedelta
from decimal import Decimal

from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.tracking.models import EtaPrediction, GeofenceEvent, GeoFence, TrackingEvent
from apps.tracking.serializers import (
    EtaPredictionSerializer,
    GeofenceEventSerializer,
    GeoFenceSerializer,
    TrackingEventSerializer,
)


class TrackingEventViewSet(TenantViewSet):
    queryset = TrackingEvent.objects.select_related("shipment", "shipment__carrier")
    serializer_class = TrackingEventSerializer
    required_permission = "tracking.view"
    write_permission = "tracking.manage"
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["shipment__number", "status", "location", "description"]
    filterset_fields = ["shipment", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        org = request.organization
        return Response(
            {
                "event_count": qs.count(),
                "shipments_tracked": qs.values("shipment").distinct().count(),
                "geofence_count": GeoFence.objects.filter(organization=org).count(),
                "geofence_alerts": GeofenceEvent.objects.filter(organization=org).count(),
                "predictions": EtaPrediction.objects.filter(organization=org).count(),
                "recent_statuses": list(
                    qs.values_list("status").annotate(count=Count("id")).order_by("-count")[:6]
                ),
            }
        )


class GeoFenceViewSet(TenantViewSet):
    queryset = GeoFence.objects.all()
    serializer_class = GeoFenceSerializer
    required_permission = "tracking.view"
    write_permission = "tracking.manage"
    search_fields = ["name"]
    filterset_fields = ["radius_m"]


class GeofenceEventViewSet(TenantViewSet):
    queryset = GeofenceEvent.objects.select_related("fence", "shipment")
    serializer_class = GeofenceEventSerializer
    required_permission = "tracking.view"
    write_permission = "tracking.manage"
    search_fields = ["fence__name", "shipment__number"]
    filterset_fields = ["fence", "shipment", "direction"]


class EtaPredictionViewSet(TenantViewSet):
    queryset = EtaPrediction.objects.select_related("shipment", "shipment__carrier")
    serializer_class = EtaPredictionSerializer
    required_permission = "tracking.view"
    write_permission = "tracking.manage"
    search_fields = ["shipment__number"]
    filterset_fields = ["shipment"]

    @action(detail=True, methods=["post"])
    def refresh(self, request, pk=None):
        """Recompute an ETA prediction for the shipment."""
        prediction = self.get_object()
        hours = int(request.data.get("hours", 6))
        prediction.eta = timezone.now() + timedelta(minutes=hours)
        prediction.confidence = Decimal(str(request.data.get("confidence", "0.7")))
        prediction.predicted_at = timezone.now()
        prediction.save(update_fields=["eta", "confidence", "predicted_at", "updated_at"])
        return Response(self.get_serializer(prediction).data)
