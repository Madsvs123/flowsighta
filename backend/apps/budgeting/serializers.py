from rest_framework import serializers

from apps.budgeting.models import Budget, BudgetActual, BudgetLine, CostCenter
from apps.core.mixins import TenantSerializer


class CostCenterSerializer(TenantSerializer):
    manager_name = serializers.CharField(source="manager.get_full_name", read_only=True)

    class Meta:
        model = CostCenter
        fields = (
            "id",
            "code",
            "name",
            "manager",
            "manager_name",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class BudgetLineSerializer(TenantSerializer):
    actual_total = serializers.SerializerMethodField()

    class Meta:
        model = BudgetLine
        fields = (
            "id",
            "budget",
            "category",
            "planned_amount",
            "actual_total",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_actual_total(self, obj):
        return float(sum((a.actual_amount or 0) for a in obj.actuals.all()))


class BudgetSerializer(TenantSerializer):
    cost_center_name = serializers.CharField(source="cost_center.name", read_only=True)
    actual_total = serializers.SerializerMethodField()
    utilization_pct = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = (
            "id",
            "name",
            "cost_center",
            "cost_center_name",
            "fiscal_year",
            "status",
            "total_amount",
            "actual_total",
            "utilization_pct",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_actual_total(self, obj):
        return float(
            sum(
                (a.actual_amount or 0)
                for line in obj.lines.all()
                for a in line.actuals.all()
            )
        )

    def get_utilization_pct(self, obj):
        planned = obj.total_amount or 0
        if not planned:
            return 0
        actual = self.get_actual_total(obj)
        return round((actual / float(planned)) * 10, 1)


class BudgetActualSerializer(TenantSerializer):
    category = serializers.CharField(source="line.category", read_only=True)

    class Meta:
        model = BudgetActual
        fields = (
            "id",
            "line",
            "category",
            "period",
            "actual_amount",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
