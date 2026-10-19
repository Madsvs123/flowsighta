from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.budgeting.models import Budget, BudgetActual, BudgetLine, CostCenter
from apps.budgeting.serializers import (
    BudgetActualSerializer,
    BudgetLineSerializer,
    BudgetSerializer,
    CostCenterSerializer,
)
from apps.core.mixins import TenantViewSet


class CostCenterViewSet(TenantViewSet):
    queryset = CostCenter.objects.select_related("manager")
    serializer_class = CostCenterSerializer
    required_permission = "budgeting.view"
    write_permission = "budgeting.manage"
    search_fields = ["code", "name"]
    filterset_fields = ["is_active", "manager"]


class BudgetViewSet(TenantViewSet):
    queryset = Budget.objects.select_related("cost_center").prefetch_related(
        "lines__actuals"
    )
    serializer_class = BudgetSerializer
    required_permission = "budgeting.view"
    write_permission = "budgeting.manage"
    search_fields = ["name", "cost_center__code", "cost_center__name"]
    filterset_fields = ["status", "fiscal_year", "cost_center"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        planned = sum((b.total_amount or 0) for b in qs)
        actual = float(
            BudgetActual.objects.filter(
                organization=request.organization, line__budget__in=qs
            ).aggregate(total=Sum("actual_amount"))["total"]
            or 0
        )
        utilization = round((actual / float(planned)) * 100, 1) if planned else 0
        return Response(
            {
                "budgets": qs.count(),
                "draft": qs.filter(status=Budget.Status.DRAFT).count(),
                "approved": qs.filter(status=Budget.Status.APPROVED).count(),
                "frozen": qs.filter(status=Budget.Status.FROZEN).count(),
                "cost_centers": CostCenter.objects.filter(
                    organization=request.organization
                ).count(),
                "planned": float(planned),
                "actual": actual,
                "utilization_pct": utilization,
            }
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        budget = self.get_object()
        if budget.status != Budget.Status.DRAFT:
            raise ValidationError("Only draft budgets can be approved.")
        budget.status = Budget.Status.APPROVED
        budget.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(budget).data)

    @action(detail=True, methods=["post"])
    def freeze(self, request, pk=None):
        budget = self.get_object()
        if budget.status != Budget.Status.FROZEN:
            raise ValidationError("Only approved budgets can be frozen.")
        budget.status = Budget.Status.FROZEN
        budget.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(budget).data)


class BudgetLineViewSet(TenantViewSet):
    queryset = BudgetLine.objects.select_related("budget").prefetch_related("actuals")
    serializer_class = BudgetLineSerializer
    required_permission = "budgeting.view"
    write_permission = "budgeting.manage"
    search_fields = ["category", "budget__name"]
    filterset_fields = ["budget"]


class BudgetActualViewSet(TenantViewSet):
    queryset = BudgetActual.objects.select_related("line", "line__budget")
    serializer_class = BudgetActualSerializer
    required_permission = "budgeting.view"
    write_permission = "budgeting.manage"
    search_fields = ["period", "line__category"]
    filterset_fields = ["line", "period"]
