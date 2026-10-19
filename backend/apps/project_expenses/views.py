from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.project_expenses.models import (
    ExpenseApproval,
    ExpenseBudget,
    ProjectBilling,
    ProjectExpense,
)
from apps.project_expenses.serializers import (
    ExpenseApprovalSerializer,
    ExpenseBudgetSerializer,
    ProjectBillingSerializer,
    ProjectExpenseSerializer,
)


class ProjectExpenseViewSet(TenantViewSet):
    queryset = ProjectExpense.objects.all()
    serializer_class = ProjectExpenseSerializer
    required_permission = "project_expenses.view"
    write_permission = "project_expenses.manage"
    search_fields = ["project_ref", "description", "vendor_ref", "category"]
    filterset_fields = ["project_ref", "category", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        budgets = ExpenseBudget.objects.filter(organization=request.organization)
        billings = ProjectBilling.objects.filter(organization=request.organization)
        return Response(
            {
                "expense_count": qs.count(),
                "pending_approval": qs.filter(status=ProjectExpense.Status.SUBMITTED).count(),
                "approved_expenses": qs.filter(status=ProjectExpense.Status.APPROVED).count(),
                "total_approved": float(
                    qs.aggregate(v=Sum("amount"))["v"] or 0
                ),
                "budget_count": budgets.count(),
                "planned_total": float(budgets.aggregate(v=Sum("planned_amount"))["v"] or 0),
                "billing_total": float(
                    billings.filter(status=ProjectBilling.Status.PAID).aggregate(v=Sum("amount"))["v"] or 0
                ),
                "by_status": {s: qs.filter(status=s).count() for s, _ in ProjectExpense.Status.choices},
            }
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        expense = self.get_object()
        expense.status = ProjectExpense.Status.APPROVED
        expense.save(update_fields=["status", "updated_at"])
        ExpenseApproval.objects.create(
            organization=expense.organization,
            expense=expense,
            approver=request.user,
            decision=ExpenseApproval.Decision.APPROVED,
            comment=request.data.get("comment", ""),
        )
        return Response(self.get_serializer(expense).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        expense = self.get_object()
        expense.status = ProjectExpense.Status.REJECTED
        expense.save(update_fields=["status", "updated_at"])
        ExpenseApproval.objects.create(
            organization=expense.organization,
            expense=expense,
            approver=request.user,
            decision=ExpenseApproval.Decision.REJECTED,
            comment=request.data.get("comment", ""),
        )
        return Response(self.get_serializer(expense).data)


class ExpenseBudgetViewSet(TenantViewSet):
    queryset = ExpenseBudget.objects.all()
    serializer_class = ExpenseBudgetSerializer
    required_permission = "project_expenses.view"
    write_permission = "project_expenses.manage"
    search_fields = ["project_ref", "category"]
    filterset_fields = ["project_ref", "category"]


class ExpenseApprovalViewSet(TenantViewSet):
    queryset = ExpenseApproval.objects.select_related("expense", "approver")
    serializer_class = ExpenseApprovalSerializer
    required_permission = "project_expenses.view"
    write_permission = "project_expenses.manage"
    http_method_names = ["get", "head", "options"]
    search_fields = ["expense__project_ref", "approver__first_name"]
    filterset_fields = ["expense", "decision", "approver"]


class ProjectBillingViewSet(TenantViewSet):
    queryset = ProjectBilling.objects.all()
    serializer_class = ProjectBillingSerializer
    required_permission = "project_expenses.view"
    write_permission = "project_expenses.manage"
    search_fields = ["project_ref"]
    filterset_fields = ["project_ref", "status"]

    @action(detail=True, methods=["post"])
    def mark_sent(self, request, pk=None):
        billing = self.get_object()
        billing.status = ProjectBilling.Status.SENT
        billing.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(billing).data)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        billing = self.get_object()
        billing.status = ProjectBilling.Status.PAID
        billing.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(billing).data
