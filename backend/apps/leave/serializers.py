from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.leave.models import LeaveApproval, LeaveBalance, LeavePolicy, LeaveRequest


class LeavePolicySerializer(TenantSerializer):
    class Meta:
        model = LeavePolicy
        fields = (
            "id",
            "name",
            "type",
            "days_per_year",
            "carryover_days",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class LeaveBalanceSerializer(TenantSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    policy_name = serializers.CharField(source="policy.name", read_only=True)

    class Meta:
        model = LeaveBalance
        fields = (
            "id",
            "employee",
            "employee_name",
            "policy",
            "policy_name",
            "year",
            "allocated",
            "used",
            "remaining",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class LeaveRequestSerializer(TenantSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    policy_name = serializers.CharField(source="policy.name", read_only=True)
    policy_type = serializers.CharField(source="policy__type", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = (
            "id",
            "employee",
            "employee_name",
            "policy",
            "policy_name",
            "policy_type",
            "start_date",
            "end_date",
            "days",
            "reason",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class LeaveApprovalSerializer(TenantSerializer):
    approver_name = serializers.CharField(source="approver.get_full_name", read_only=True)

    class Meta:
        model = LeaveApproval
        fields = ("id", "request", "approver", "approver_name", "decision", "comment", "decided_at", "created_at")
        read_only_fields = ("id", "created_at")
