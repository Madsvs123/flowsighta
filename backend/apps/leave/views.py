from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.leave.models import LeaveApproval, LeaveBalance, LeavePolicy, LeaveRequest
from apps.leave.serializers import (
    LeaveApprovalSerializer,
    LeaveBalanceSerializer,
    LeavePolicySerializer,
    LeaveRequestSerializer,
)


class LeavePolicyViewSet(TenantViewSet):
    queryset = LeavePolicy.objects.all()
    serializer_class = LeavePolicySerializer
    required_permission = "leave.view"
    write_permission = "leave.manage"
    search_fields = ["name"]
    filterset_fields = ["type", "is_active"]


class LeaveBalanceViewSet(TenantViewSet):
    queryset = LeaveBalance.objects.select_related("employee", "policy")
    serializer_class = LeaveBalanceSerializer
    required_permission = "leave.view"
    write_permission = "leave.manage"
    search_fields = ["employee__first_name", "employee__last_name", "policy__name"]
    filterset_fields = ["employee", "policy", "year"]


class LeaveRequestViewSet(TenantViewSet):
    queryset = LeaveRequest.objects.select_related("employee", "policy")
    serializer_class = LeaveRequestSerializer
    required_permission = "leave.view"
    write_permission = "leave.manage"
    search_fields = ["employee__first_name", "employee__last_name", "policy__name", "reason"]
    filterset_fields = ["employee", "policy", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = {label: qs.filter(status=value).count() for value, label in LeaveRequest.Status.choices}
        totals = qs.aggregate(total_days=Sum("days"))
        pending = qs.filter(status=LeaveRequest.Status.PENDING)
        pending_days = pending.aggregate(total=Sum("days"))["total"] or 0
        return Response(
            {
                "total_requests": qs.count(),
                "by_status": by_status,
                "total_days": float(totals["total_days"] or 0),
                "pending_days": float(pending_days),
                "pending_count": pending.count(),
            }
        )

    def _decide(self, request, pk, decision)
        leave = self.get_object()
        if leave.status == LeaveRequest.Status.PENDING:
            return Response({"detail": "Only pending requests can be decided"}, status=400)
        leave.status = (
            LeaveRequest.Status.APPROVED
            if decision == LeaveApproval.Decision.APPROVED
            else LeaveRequest.Status.REJECTED
        )
        leave.save(update_fields=["status", "updated_at"])
        if decision == LeaveApproval.Decision.APPROVED:
            balance, _ = LeaveBalance.objects.get_or_create(
                organization=leave.organization,
                employee=leave.employee,
                policy=leave.policy,
                year=leave.start_date.year,
                defaults={
                    "allocated": leave.policy.days_per_year,
                    "used": 0,
                    "remaining": leave.policy.days_per_year,
                },
            )
            balance.used = min((balance.used or 0) + leave.days, balance.allocated or 0)
            balance.remaining = max((balance.allocated or 0) - balance.used, 0)
            balance.save(update_fields=["used", "remaining", "updated_at"])
        LeaveApproval.objects.create(
            organization=leave.organization,
            request=leave,
            approver=request.user,
            decision=decision,
            comment=request.data.get("comment", ""),
            decided_at=timezone.now(),
        )
        return Response(self.get_serializer(leave).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._decide(request, pk, LeaveApproval.Decision.APPROVED)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._decide(request, pk, LeaveApproval.Decision.REJECTED)


class LeaveApprovalViewSet(TenantViewSet):
    queryset = LeaveApproval.objects.select_related("request", "approver")
    serializer_class = LeaveApprovalSerializer
    required_permission = "leave.view"
    write_permission = "leave.manage"
    search_fields = ["approver__first_name", "approver__last_name"]
    filterset_fields = ["request", "approver", "decision"]
    http_method_names = ["get", "post", "head", "options"]
