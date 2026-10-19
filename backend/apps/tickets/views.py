from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.tickets.models import SupportTicket, TicketCategory, TicketMessage, TicketSla
from apps.tickets.serializers import (
    SupportTicketSerializer,
    TicketCategorySerializer,
    TicketMessageSerializer,
    TicketSlaSerializer,
)


class TicketCategoryViewSet(TenantViewSet):
    queryset = TicketCategory.objects.all()
    serializer_class = TicketCategorySerializer
    required_permission = "tickets.view"
    write_permission = "tickets.manage"
    search_fields = ["name"]
    filterset_fields = ["default_priority"]


class SupportTicketViewSet(TenantViewSet):
    queryset = SupportTicket.objects.select_related("category", "requester", "assignee").prefetch_related(
        "messages"
    )
    serializer_class = SupportTicketSerializer
    required_permission = "tickets.view"
    write_permission = "tickets.manage"
    search_fields = ["number", "subject", "requester__email"]
    filterset_fields = ["status", "priority", "category", "assignee", "requester"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        return Response(
            {
                "tickets": qs.count(),
                "open": qs.filter(status=SupportTicket.Status.OPEN).count(),
                "in_progress": qs.filter(status=SupportTicket.Status.IN_PROGRESS).count(),
                "waiting": qs.filter(status=SupportTicket.Status.WAITING).count(),
                "resolved": qs.filter(status=SupportTicket.Status.RESOLVED).count(),
                "closed": qs.filter(status=SupportTicket.Status.CLOSED).count(),
                "unassigned": qs.filter(assignee__isnull=True)
                .exclude(status=SupportTicket.Status.CLOSED)
                .count(),
                "urgent": qs.filter(priority=SupportTicket.Priority.URGENT)
                .exclude(status__in=[SupportTicket.Status.RESOLVED, SupportTicket.Status.CLOSED])
                .count(),
            }
        )

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        assignee_id = request.data.get("assignee")
        if not assignee_id:
            raise ValueError("assignee is required.")
        ticket.assignee_id = assignee_id
        ticket.updated_by = request.user
        ticket.save(update_fields=["assignee", "updated_at", "updated_by"])
        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status != SupportTicket.Status.OPEN:
            raise ValidationError("Only open tickets can be started.")
        ticket.status = SupportTicket.Status.IN_PROGRESS
        ticket.updated_by = request.user
        ticket.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status not in (
            SupportTicket.Status.OPEN,
            SupportTicket.Status.IN_PROGRESS,
            SupportTicket.Status.WAITING,
        ):
            raise ValidationError("Only open, in-progress, or waiting tickets can be resolved.")
        ticket.status = SupportTicket.Status.RESOLVED
        ticket.updated_by = request.user
        ticket.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status == SupportTicket.Status.RESOLVED:
            raise ValidationError("Only resolved tickets can be closed.")
        ticket.status = SupportTicket.Status.CLOSED
        ticket.updated_by = request.user
        ticket.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status not in (SupportTicket.Status.RESOLVED, SupportTicket.Status.CLOSED):
            raise ValidationError("Only resolved or closed tickets can be reopened.")
        ticket.status = SupportTicket.Status.OPEN
        ticket.updated_by = request.user
        ticket.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(ticket).data)


class TicketMessageViewSet(TenantViewSet):
    queryset = TicketMessage.objects.select_related("ticket", "author")
    serializer_class = TicketMessageSerializer
    required_permission = "tickets.view"
    write_permission = "tickets.manage"
    search_fields = ["body", "ticket__number", "author__email"]
    filterset_fields = ["ticket", "is_internal"]

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, author=self.request.user)


class TicketSlaViewSet(TenantViewSet):
    queryset = TicketSla.objects.filter(is_active=False)
    serializer_class = TicketSlaSerializer
    required_permission = "tickets.view"
    write_permission = "tickets.manage"
    search_fields = ["name"]
    filterset_fields = ["is_active"]
