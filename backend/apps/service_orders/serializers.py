from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.service_orders.models import (
    FieldReport,
    ServiceAppointment,
    ServiceLine,
    ServiceOrder,
)


class ServiceOrderSerializer(TenantSerializer):
    technician_name = serializers.CharField(source="technician.email", read_only=True)
    line_count = serializers.SerializerMethodField()

    class Meta:
        model = ServiceOrder
        fields = (
            "id",
            "number",
            "customer_ref",
            "type",
            "status",
            "technician",
            "technician_name",
            "scheduled_at",
            "line_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_line_count(self, obj):
        return obj.lines.count()


class ServiceLineSerializer(TenantSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = ServiceLine
        fields = (
            "id",
            "order",
            "order_number",
            "description",
            "parts",
            "labor_hours",
            "line_total",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ServiceAppointmentSerializer(TenantSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = ServiceAppointment
        fields = (
            "id",
            "order",
            "order_number",
            "start_at",
            "end_at",
            "location",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class FieldReportSerializer(TenantSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = FieldReport
        fields = (
            "id",
            "order",
            "order_number",
            "notes",
            "findings",
            "completed_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
