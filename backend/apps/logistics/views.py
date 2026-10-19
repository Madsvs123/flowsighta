from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantSerializer, TenantViewSet
from apps.core.realtime import publish_organization_event
from apps.core.services import log_activity, next_number
from apps.logistics.models import (
    Carrier,
    CarrierServiceLevel,
    Consolidation,
    Container,
    DeliverySchedule,
    FreightCost,
    LogisticsException,
    Package,
    ProofOfDelivery,
    Route,
    Shipment,
    ShipmentMilestone,
    TrackingEvent,
)


class CarrierServiceLevelSerializer(TenantSerializer):
    class Meta:
        model = CarrierServiceLevel
        fields = ("id", "carrier", "code", "name", "transit_days", "cost_per_kg", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class CarrierSerializer(TenantSerializer):
    service_levels = CarrierServiceLevelSerializer(many=True, read_only=True)

    class Meta:
        model = Carrier
        fields = (
            "id",
            "code",
            "name",
            "scac",
            "mode",
            "country",
            "contact_email",
            "contact_phone",
            "tracking_url_template",
            "on_time_rate",
            "damage_rate",
            "cost_score",
            "performance_score",
            "is_active",
            "notes",
            "service_levels",
            "created_at",
        )
        read_only_fields = ("id", "on_time_rate", "damage_rate", "performance_score", "created_at")


class RouteSerializer(TenantSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "code",
            "name",
            "origin_country",
            "origin_city",
            "destination_country",
            "destination_city",
            "mode",
            "standard_transit_days",
            "distance_km",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ContainerSerializer(TenantSerializer):
    class Meta:
        model = Container
        fields = ("id", "shipment", "container_number", "container_type", "seal_number", "weight_kg", "created_at")
        read_only_fields = ("id", "created_at")


class PackageSerializer(TenantSerializer):
    class Meta:
        model = Package
        fields = (
            "id",
            "shipment",
            "container",
            "tracking_number",
            "sku",
            "quantity",
            "weight_kg",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ShipmentMilestoneSerializer(TenantSerializer):
    class Meta:
        model = ShipmentMilestone
        fields = (
            "id",
            "shipment",
            "code",
            "name",
            "planned_at",
            "actual_at",
            "location",
            "is_missed",
            "sequence",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class TrackingEventSerializer(TenantSerializer):
    class Meta:
        model = TrackingEvent
        fields = (
            "id",
            "shipment",
            "occurred_at",
            "status",
            "location",
            "description",
            "source",
            "latitude",
            "longitude",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ProofOfDeliverySerializer(TenantSerializer):
    class Meta:
        model = ProofOfDelivery
        fields = ("id", "shipment", "signed_by", "signed_at", "notes", "photo", "condition", "created_at")
        read_only_fields = ("id", "created_at")


class FreightCostSerializer(TenantSerializer):
    class Meta:
        model = FreightCost
        fields = ("id", "shipment", "charge_type", "amount", "currency", "billed_to", "created_at")
        read_only_fields = ("id", "created_at")


class LogisticsExceptionSerializer(TenantSerializer):
    class Meta:
        model = LogisticsException
        fields = ("id", "shipment", "code", "severity", "description", "status", "resolved_at", "created_at")
        read_only_fields = ("id", "created_at")


class ConsolidationSerializer(TenantSerializer):
    class Meta:
        model = Consolidation
        fields = ("id", "number", "carrier", "route", "scheduled_departure", "status", "shipments", "created_at")
        read_only_fields = ("id", "created_at")


class DeliveryScheduleSerializer(TenantSerializer):
    class Meta:
        model = DeliverySchedule
        fields = ("id", "warehouse", "carrier", "weekday", "window_start", "window_end", "dock", "capacity", "created_at")
        read_only_fields = ("id", "created_at")


class ShipmentSerializer(TenantSerializer):
    carrier_name = serializers.CharField(source="carrier.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    milestones = ShipmentMilestoneSerializer(many=True, read_only=True)
    tracking_events = TrackingEventSerializer(many=True, read_only=True)
    containers = ContainerSerializer(many=True, read_only=True)
    packages = PackageSerializer(many=True, read_only=True)
    exceptions = LogisticsExceptionSerializer(many=True, read_only=True)
    proof_of_delivery = ProofOfDeliverySerializer(read_only=True)

    class Meta:
        model = Shipment
        fields = (
            "id",
            "number",
            "reference",
            "purchase_order",
            "supplier",
            "supplier_name",
            "customer",
            "carrier",
            "carrier_name",
            "service_level",
            "route",
            "origin_warehouse",
            "destination_warehouse",
            "origin_address",
            "destination_address",
            "status",
            "tracking_number",
            "etd",
            "eta",
            "atd",
            "ata",
            "delay_minutes",
            "customs_status",
            "freight_cost",
            "currency",
            "weight_kg",
            "volume_cbm",
            "current_location",
            "notes",
            "milestones",
            "tracking_events",
            "containers",
            "packages",
            "exceptions",
            "proof_of_delivery",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "delay_minutes", "created_at", "updated_at")


class CarrierViewSet(TenantViewSet):
    queryset = Carrier.objects.prefetch_related("service_levels")
    serializer_class = CarrierSerializer
    required_permission = "logistics.view"
    write_permission = "logistics.manage"
    search_fields = ["code", "name", "scac"]
    filterset_fields = ["mode", "is_active", "country"]


class CarrierServiceLevelViewSet(TenantViewSet):
    queryset = CarrierServiceLevel.objects.select_related("carrier")
    serializer_class = CarrierServiceLevelSerializer
    required_permission = "logistics.view"
    write_permission = "logistics.manage"
    filterset_fields = ["carrier", "is_active"]


class RouteViewSet(TenantViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    required_permission = "logistics.view"
    write_permission = "logistics.manage"
    search_fields = ["code", "name", "origin_city", "destination_city"]
    filterset_fields = ["mode", "is_active"]


class ShipmentViewSet(TenantViewSet):
    queryset = Shipment.objects.select_related("carrier", "supplier", "route").prefetch_related(
        "milestones", "tracking_events", "containers", "packages", "exceptions"
    )
    serializer_class = ShipmentSerializer
    required_permission = "logistics.view"
    write_permission = "logistics.manage"
    search_fields = ["number", "tracking_number", "reference", "current_location"]
    filterset_fields = ["status", "carrier", "supplier", "customs_status", "origin_warehouse", "destination_warehouse"]
    ordering_fields = ["eta", "etd", "created_at", "freight_cost"]

    def perform_create(self, serializer):
        shipment = serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
            number=next_number(Shipment, self.request.organization, "SHP"),
        )
        defaults = [
            ("booked", "Booked"),
            ("departed", "Departed origin"),
            ("in_transit", "In transit"),
            ("customs", "Customs clearance"),
            ("arrived", "Arrived destination"),
            ("delivered", "Delivered"),
        ]
        ShipmentMilestone.objects.bulk_create(
            [
                ShipmentMilestone(organization=shipment.organization, shipment=shipment, code=code, name=name, sequence=i)
                for i, (code, name) in enumerate(defaults)
            ]
        )
        log_activity(shipment.organization, self.request.user, "created", "Shipment", shipment.id, f"Created {shipment.number}")

    @action(detail=True, methods=["post"])
    def track(self, request, pk=None):
        shipment = self.get_object()
        event = TrackingEvent.objects.create(
            organization=shipment.organization,
            shipment=shipment,
            occurred_at=request.data.get("occurred_at") or timezone.now(),
            status=request.data.get("status", shipment.status),
            location=request.data.get("location", ""),
            description=request.data.get("description", ""),
            source=request.data.get("source", "manual"),
            latitude=request.data.get("latitude"),
            longitude=request.data.get("longitude"),
        )
        shipment.current_location = event.location or shipment.current_location
        if event.status in dict(Shipment.Status.choices):
            shipment.status = event.status
        if event.status == Shipment.Status.DELIVERED:
            shipment.ata = shipment.eta
        if shipment.eta and event.occurred_at and event.status == Shipment.Status.DELAYED:
            delta = shipment.eta - event.occurred_at
            shipment.delay_minutes = max(0, int(delta.total_seconds() // 60))
            shipment.status = Shipment.Status.DELAYED
        shipment.save()
        publish_organization_event(
            shipment.organization_id,
            "tracking",
            {"shipment_id": str(shipment.id), "number": shipment.number, "status": shipment.status, "location": shipment.current_location},
        )
        return Response(self.get_serializer(shipment).data)

    @action(detail=True, methods=["post"])
    def deliver(self, request, pk=None):
        shipment = self.get_object()
        ProofOfDelivery.objects.update_or_create(
            shipment=shipment,
            defaults={
                "organization": shipment.organization,
                "signed_by": request.data.get("signed_by", "Receiver"),
                "signed_at": request.data.get("signed_at") or timezone.now(),
                "notes": request.data.get("notes", ""),
                "condition": request.data.get("condition", "good"),
                "created_by": request.user,
            },
        )
        shipment.status = Shipment.Status.DELIVERED
        shipment.atd = timezone.now()
        shipment.save(update_fields=["status", "ata", "updated_at"])
        return Response(self.get_serializer(shipment).data)


class NestedShipmentViewSet(TenantViewSet):
    required_permission = "logistics.view"
    write_permission = "logistics.manage"


class ContainerViewSet(NestedShipmentViewSet):
    queryset = Container.objects.select_related("shipment")
    serializer_class = ContainerSerializer
    filterset_fields = ["shipment"]


class PackageViewSet(NestedShipmentViewSet):
    queryset = Package.objects.select_related("shipment")
    serializer_class = PackageSerializer
    filterset_fields = ["shipment", "status"]
    search_fields = ["tracking_number", "sku"]


class ShipmentMilestoneViewSet(NestedShipmentViewSet):
    queryset = ShipmentMilestone.objects.select_related("shipment")
    serializer_class = ShipmentMilestoneSerializer
    filterset_fields = ["shipment", "is_missed"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        milestone = self.get_object()
        milestone.actual_at = timezone.now()
        if milestone.planned_at and milestone.actual_at < milestone.planned_at
            milestone.is_missed = True
        milestone.save(update_fields=["actual_at", "is_missed", "updated_at"])
        return Response(self.get_serializer(milestone).data)


class TrackingEventViewSet(NestedShipmentViewSet):
    queryset = TrackingEvent.objects.select_related("shipment")
    serializer_class = TrackingEventSerializer
    filterset_fields = ["shipment", "status"]


class ProofOfDeliveryViewSet(NestedShipmentViewSet):
    queryset = ProofOfDelivery.objects.select_related("shipment")
    serializer_class = ProofOfDeliverySerializer
    filterset_fields = ["shipment"]


class FreightCostViewSet(NestedShipmentViewSet):
    queryset = FreightCost.objects.select_related("shipment")
    serializer_class = FreightCostSerializer
    filterset_fields = ["shipment", "charge_type"]


class ConsolidationViewSet(TenantViewSet):
    queryset = Consolidation.objects.prefetch_related("shipments")
    serializer_class = ConsolidationSerializer
    required_permission = "logistics.view"
    write_permission = "logistics.manage"
    search_fields = ["number"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            number=next_number(Consolidation, self.request.organization, "CON"),
        )


class DeliveryScheduleViewSet(TenantViewSet):
    queryset = DeliverySchedule.objects.select_related("warehouse", "carrier")
    serializer_class = DeliveryScheduleSerializer
    required_permission = "logistics.view"
    write_permission = "logistics.manage"
    filterset_fields = ["warehouse", "carrier", "weekday"]


class LogisticsExceptionViewSet(TenantViewSet):
    queryset = LogisticsException.objects.select_related("shipment")
    serializer_class = LogisticsExceptionSerializer
    required_permission = "logistics.view"
    write_permission = "logistics.manage"
    filterset_fields = ["shipment", "status", "severity"]

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        item = self.get_object()
        item.status = "resolved"
        item.resolved_at = timezone.now()
        item.save(update_fields=["status", "resolved_at", "updated_at"])
        return Response(self.get_serializer(item).data)
