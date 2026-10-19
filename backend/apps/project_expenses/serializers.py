from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.project_expenses.models import (
    ExpenseApproval,
    ExpenseBudget,
    ProjectBilling,
    ProjectExpense,
)


class ProjectExpenseSerializer(TenantSerializer):
    class Meta:
        model = ProjectExpense
        fields = (
            "id",
            "project_ref",
            "category",
            "date",
            "description",
            "amount",
            "vendor_ref",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ExpenseBudgetSerializer(TenantSerializer):
    class Meta:
        model = ExpenseBudget
        fields = ("id", "project_ref", "category", "planned_amount", "created_at")
        read_only_fields = ("id", "created_at")


class ExpenseApprovalSerializer(TenantSerializer):
    expense_ref = serializers.CharField(source="expense.project_ref", read_only=True)
    approver_name = serializers.CharField(source="approver.get_fullname", read_only=True)

    class Meta:
        model = ExpenseApproval
        fields = (
            "id",
            "expense",
            "expense_ref",
            "approver",
            "approver_name",
            "decision",
            "comment",
            "decided_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ProjectBillingSerializer(TenantSerializer):
    class Meta:
        model = ProjectBilling
        fields = (
            "id",
            "project_ref",
            "rate",
            "hours",
            "amount",
            "billing_date",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
