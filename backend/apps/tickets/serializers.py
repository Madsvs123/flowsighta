from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.tickets.models import SupportTicket, TicketCategory, TicketMessage, TicketSla


class TicketCategorySerializer(TenantSerializer):
    class Meta:
        model = TicketCategory
        fields = ("id", "name", "default_priority", "created_at")
        read_only_fields = ("id", "created_at")


class SupportTicketSerializer(TenantSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    requester_name = serializers.CharField(source="requester.email", read_only=True)
    assignee_name = serializers.CharField(source="assignee.email", read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = SupportTicket
        fields = (
            "id",
            "number",
            "subject",
            "category",
            "category_name",
            "status",
            "priority",
            "requester",
            "requester_name",
            "assignee",
            "assignee_name",
            "message_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_message_count(self, obj):
        return obj.messages.filter(is_internal=False).count()


class TicketMessageSerializer(TenantSerializer):
    ticket_number = serializers.CharField(source="ticket.number", read_only=True)
    author_name = serializers.CharField(source="author.email", read_only=True)

    class Meta:
        model = TicketMessage
        fields = (
            "id",
            "ticket",
            "ticket_number",
            "author",
            "author_name",
            "body",
            "is_internal",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class TicketSlaSerializer(TenantSerializer):
    class Meta:
        model = TicketSla
        fields = (
            "id",
            "name",
            "response_minutes",
            "resolution_minutes",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
