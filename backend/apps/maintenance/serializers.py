from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.maintenance.models import Equipment, MaintenanceLog, MaintenanceOrder, MaintenancePlan


class EquipmentSerializer(TenantSerializer):
    plan_count = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()

    class Meta:
        model = Equipment
        fields = (
            "id",
            "code",
            "name",
            "type",
            "location",
            "status",
            "install_date",
            "plan_count",
            "order_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_plan_count(self, obj):
        return obj.maintenance_plans.filter(is_active=True).count()

    def get_order_count(self, obj):
        return obj.maintenance_orders.count()


class MaintenancePlanSerializer(TenantSerializer):
    equipment_code = serializers.CharField(source="equipment.code", read_only=True)
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)

    class Meta:
        model = MaintenancePlan
        fields = (
            "id",
            "equipment",
            "equipment_code",
            "equipment_name",
            "frequency_days",
            "type",
            "description",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class MaintenanceOrderSerializer(TenantSerializer):
    equipment_code = serializers.CharField(source="equipment.code", read_only=True)
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)
    plan_type = serializers.CharField(source="plan.type", read_only=True)
    log_count = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceOrder
        fields = (
            "id",
            "plan",
            "plan_type",
            "equipment",
            "equipment_code",
            "equipment_name",
            "status",
            "scheduled_date",
            "completed_date",
            "cost",
            "log_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_log_count(self, obj):
        return obj.logs.count()


class MaintenanceLogSerializer(TenantSerializer):
    order_equipment = serializers.CharField(source="order.equipment.name", read_only=True)
    performed_by_name = serializers.CharField(source="performed_by.get_full_name", read_only=True)

    class Meta:
        model = MaintenanceLog
        fields = (
            "id",
            "order",
            "order_equipment",
            "notes",
            "performed_by",
            "performed_by_name",
            "hours",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
