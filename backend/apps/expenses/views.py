from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.core.services import next_number
from apps.expenses.models import ExpenseApproval, ExpenseLine, ExpenseReport, Reimbursement
from apps.expenses.serializers import (
    ExpenseApprovalSerializer,
    ExpenseLineSerializer,
    ExpenseReportSerializer,
    ReimbursementSerializer,
)


class ExpenseReportViewSet(TenantViewSet):
    queryset = ExpenseReport.objects.select_related("employee").prefetch_related("lines", "approvals")
    serializer_class = ExpenseReportSerializer
    required_permission = "expenses.view"
    write_permission = "expenses.manage"
    search_fields = ["number"]
    filterset_fields = ["status", "employee"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
            employee=self.request.user,
            number=next_number(ExpenseReport, self.request.organization, "EXP"),
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = dict(qs.values_list("status").annotate(count=Count("id")))
        totals = qs.aggregate(total=Sum("total"))
        return Response(
            {
                "reports": qs.count(),
                "draft": by_status.get("draft", 0),
                "submitted": by_status.get("submitted", 0),
                "approved": by_status.get("approved", 0),
                "paid": by_status.get("paid", 0),
                "rejected": by_status.get("rejected", 0),
                "total": totals["total"] or 0,
                "outstanding": qs.filter(status__in=[ExpenseReport.Status.SUBMITTED])
                .aggregate(total=Sum("total"))["total"]
                or 0,
                "lines": ExpenseLine.objects.filter(report__organization=request.organization).count(),
                "reimbursements": Reimbursement.objects.filter(report__organization=request.organization).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        report = self.get_object()
        report.status = ExpenseReport.Status.SUBMITTED
        report.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(report).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        report = self.get_object()
        report.status = ExpenseReport.Status.APPROVED
        report.save(update_fields=["status", "updated_at"])
        ExpenseApproval.objects.create(
            organization=report.organization,
            report=report,
            approver=request.user,
            decision=ExpenseApproval.Decision.REJECTED,
            created_by=request.user,
            updated_by=request.user,
        )
        return Response(self.get_serializer(report).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        report = self.get_object()
        report.status = ExpenseReport.Status.REJECTED
        report.save(update_fields=["status", "updated_at"])
        ExpenseApproval.objects.create(
            organization=report.organization,
            report=report,
            approver=request.user,
            decision=ExpenseApproval.Decision.REJECTED,
            comment=request.data.get("comment", ""),
            created_by=request.user,
            updated_by=request.user,
        )
        return Response(self.get_serializer(report).data)

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        report = self.get_object()
        report.status = ExpenseReport.Status.PAID
        report.save(update_fields=["status", "updated_at"])
        Reimbursement.objects.create(
            organization=report.organization,
            report=report,
            payment_ref=request.data.get("payment_ref", ""),
            amount=report.total,
            paid_at=timezone.now(),
        )
        return Response(self.get_serializer(report).data)


class ExpenseLineViewSet(TenantViewSet):
    queryset = ExpenseLine.objects.select_related("report")
    serializer_class = ExpenseLineSerializer
    required_permission = "expenses.view"
    write_permission = "expenses.manage"
    filterset_fields = ["report", "category"]


class ExpenseApprovalViewSet(TenantViewSet):
    queryset = ExpenseApproval.objects.select_related("report", "approver")
    serializer_class = ExpenseApprovalSerializer
    required_permission = "expenses.view"
    write_permission = "expenses.manage"
    filterset_fields = ["report", "approver", "decision"]


class ReimbursementViewSet(TenantViewSet):
    queryset = Reimbursement.objects.select_related("report")
    serializer_class = ReimbursementSerializer
    required_permission = "expenses.view"
    write_permission = "expenses.manage"
    filterset_fields = ["report"]
