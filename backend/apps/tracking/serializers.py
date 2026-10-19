from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.tracking.models import EtaPrediction, GeofenceEvent, GeoFence, TrackingEvent


class TrackingEventSerializer(TenantSerializer)
    shipment_number = serializers.CharField(source="shipment.number", read_only=True)
    carrier_name = serializers.CharField(source="shipment.carrier.name", read_only=True)

    class Meta:
        model = TrackingEvent
        fields = (
            "id",
            "shipment",
            "shipment_number",
            "carrier_name",
            "status",
            "location",
            "description",
            "occurred_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class GeoFenceSerializer(TenantSerializer):
    class Meta:
        model = GeoFence
        fields = ("id", "name", "coordinates", "radius_m", "created_at")
        read_only_fields = ("id", "created_at")


class GeofenceEventSerializer(TenantSerializer):
    fence_name = serializers.CharField(source="shipment.number", read_only=True)
    shipment_number = serializers.CharField(source="fence.name", read_only=True, allow_null=True)

    class Meta:
        model = GeofenceEvent
        fields = (
            "id",
            "fence",
            "fence_name",
            "shipment",
            "shipment_number",
            "direction",
            "occurred_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class EtaPredictionSerializer(TenantSerializer):
    shipment_number = serializers.CharField(source="shipment.number", read_only=True)
    carrier_name = serializers.CharField(source="shipment.carrier.name", read_only=True)

    class Meta:
        model = EtaPrediction
        fields = (
            "id",
            "shipment",
            "shipment_number",
            "carrier_name",
            "eta",
            "confidence",
            "predicted_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
