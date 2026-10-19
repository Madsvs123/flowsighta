from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantSerializer, TenantViewSet
from apps.core.realtime import publish_organization_event
from apps.core.services import next_number, notify_user
from apps.events.models import AlertRule, ResolutionAction, SupplyChainEvent
from apps.organizations.models import Membership


class ResolutionActionSerializer(TenantSerializer):
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)

    class Meta:
        model = ResolutionAction
        fields = ("id", "event", "action_type", "note", "is_complete", "completed_at", "owner", "owner_name", "created_at")
        read_only_fields = ("id", "created_at")


class SupplyChainEventSerializer(TenantSerializer):
    actions = ResolutionActionSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    assignee_name = serializers.CharField(source="assignee.full_name", read_only=True)

    class Meta:
        model = SupplyChainEvent
        fields = (
            "id",
            "number",
            "title",
            "category",
            "severity",
            "status",
            "description",
            "source_type",
            "source_id",
            "supplier",
            "supplier_name",
            "shipment",
            "warehouse",
            "product_sku",
            "detected_at",
            "acknowledged_at",
            "resolved_at",
            "assignee",
            "assignee_name",
            "impact_score",
            "metadata",
            "actions",
            "created_at",
        )
        read_only_fields = ("id", "number", "detected_at", "acknowledged_at", "resolved_at", "created_at")


class AlertRuleSerializer(TenantSerializer):
    class Meta:
        model = AlertRule
        fields = ("id", "name", "category", "is_active", "severity", "condition", "notify_roles", "created_at")
        read_only_fields = ("id", "created_at")


class SupplyChainEventViewSet(TenantViewSet):
    queryset = SupplyChainEvent.objects.select_related("supplier", "assignee").prefetch_related("actions")
    serializer_class = SupplyChainEventSerializer
    required_permission = "events.view"
    write_permission = "events.resolve"
    search_fields = ["number", "title", "product_sku", "description"]
    filterset_fields = ["category", "severity", "status", "supplier", "warehouse", "assignee"]
    ordering_fields = ["detected_at", "severity", "impact"]

    def perform_create(self, serializer)
        event = serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            number=next_number(SupplyChainEvent, self.request.organization, "EVT"),
            detected_at=timezone.now(),
        )
        publish_organization_event(
            event.organization_id,
            "alert",
            {"id": str(event.id), "title": event.title, "severity": event.severity, "category": event.category},
        )
        members = Membership.objects.filter(organization=event.organization, is_active=True).select_related("user")
        for m in members:
            if m.has_permission("events.view"):
                notify_user(
                    event.organization,
                    m.user,
                    event.title,
                    event.description,
                    category="alert",
                    severity=event.severity,
                    link=f"/alerts/{event.id}",
                )

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        event = self.get_object()
        event.status = SupplyChainEvent.Status.OPEN
        event.acknowledged_at = timezone.now()
        event.assignee = event.assignee or request.user
        event.save(update_fields=["status", "acknowledged_at", "assignee", "updated_at"])
        return Response(self.get_serializer(event).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        event = self.get_object()
        event.status = SupplyChainEvent.Status.RESOLVED
        event.resolved_at = timezone.now()
        event.save(update_fields=["status", "resolved_at", "updated_at"])
        ResolutionAction.objects.create(
            organization=event.organization,
            event=event,
            action_type="resolve",
            note=request.data.get("notes", "Resolved"),
            is_complete=True,
            completed_at=timezone.now(),
            owner=request.user,
        )
        return Response(self.get_serializer(event).data)


class AlertRuleViewSet(TenantViewSet):
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    required_permission = "events.view"
    write_permission = "events.resolve"
    filterset_fields = ["is_active", "category"]


class ResolutionActionViewSet(TenantViewSet):
    queryset = ResolutionAction.objects.select_related("event", "owner")
    serializer_class = ResolutionActionSerializer
    required_permission = "events.view"
    write_permission = "events.resolve"
    filterset_fields = ["event", "is_complete"]
