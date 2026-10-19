from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.work_orders.models import WorkOrder, WorkOrderLabor, WorkOrderTask


class WorkOrderTaskSerializer(TenantSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)

    class Meta:
        model = WorkOrderTask
        fields = (
            "id",
            "order",
            "order_number",
            "description",
            "status",
            "duration_minutes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class WorkOrderLaborSerializer(TenantSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = WorkOrderLabor
        fields = (
            "id",
            "order",
            "order_number",
            "user",
            "user_name",
            "hours",
            "date",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class WorkOrderSerializer(TenantSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    task_count = serializers.SerializerMethodField()
    labor_hours = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = (
            "id",
            "number",
            "type",
            "status",
            "priority",
            "assigned_to",
            "assigned_to_name",
            "due_date",
            "task_count",
            "labor_hours",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_task_count(self, obj):
        return obj.tasks.count()

    def get_labor_hours(self, obj):
        return sum(l.hours or 0 for l in obj.labor.all())
