from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.expenses.models import ExpenseApproval, ExpenseLine, ExpenseReport, Reimbursement


class ExpenseLineSerializer(TenantSerializer):
    class Meta:
        model = ExpenseLine
        fields = (
            "id",
            "report",
            "category",
            "date",
            "description",
            "amount",
            "receipt_ref",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ExpenseApprovalSerializer(TenantSerializer):
    approver_name = serializers.CharField(source="approver.full_name", read_only=True)

    class Meta:
        model = ExpenseApproval
        fields = (
            "id",
            "report",
            "approver",
            "approver_name",
            "decision",
            "comment",
            "decided_at",
            "created_at",
        )
        read_only_fields = ("id", "decided_at", "created_at")


class ReimbursementSerializer(TenantSerializer):
    report_number = serializers.CharField(source="report.number", read_only=True)

    class Meta:
        model = Reimbursement
        fields = (
            "id",
            "report",
            "report_number",
            "payment_ref",
            "amount",
            "paid_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ExpenseReportSerializer(TenantSerializer):
    lines = ExpenseLineSerializer(many=True, required=False)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    line_count = serializers.SerializerMethodField()
    latest_approval = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseReport
        fields = (
            "id",
            "number",
            "employee",
            "employee_name",
            "status",
            "total",
            "line_count",
            "latest_approval",
            "lines",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "number", "status", "total", "created_at", "updated_at")

    def get_line_count(self, obj):
        return getattr(obj, "_line_count", None) or obj.lines.all()

    def get_latest_approval(self, obj):
        latest = obj.approvals.order_by("decided_at").first()
        return latest.decision if latest else None

    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        instance = super().create(validated_data)
        total = Decimal("0")
        for line in lines:
            line.pop("report", None)
            ExpenseLine.objects.create(organization=instance.organization, report=instance, **line)
            total += Decimal(str(line.get("amount") or 0))
        instance.total = total
        instance.save(update_fields=["total"])
        return instance
