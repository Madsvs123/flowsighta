from rest_framework.routers import DefaultRouter

from apps.expenses.views import (
    ExpenseApprovalViewSet,
    ExpenseLineViewSet,
    ExpenseReportViewSet,
    ReimbursementViewSet,
)

router = DefaultRouter()
router.register("expense-report", ExpenseReportViewSet, basename="expense-reports")
router.register("expense-lines", ExpenseLineViewSet, basename="expense-lines")
router.register("expense-approvals", ExpenseApprovalViewSet, basename="expense-approvals")
router.register("reimbursements", ReimbursementViewSet, basename="reimbursements")

urlpatterns = router.urls
