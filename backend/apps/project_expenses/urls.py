from rest_framework.routers import DefaultRouter

from apps.project_expenses.views import (
    ExpenseApprovalViewSet,
    ExpenseBudgetViewSet,
    ProjectBillingViewSet,
    ProjectExpenseViewSet,
)

router = DefaultRouter()
router.register("project-expenses", ProjectExpenseViewSet, basename="projectexpense")
router.register("expense-budgets", ExpenseBudgetViewSet, basename="expense-budget")
router.register("expense-approvals", ExpenseApprovalViewSet, basename="expenseapproval")
router.register("project-billings", ProjectBillingViewSet, basename="projectbilling")

urlpatterns = router.urls
