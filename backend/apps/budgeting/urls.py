from rest_framework.routers import DefaultRouter

from apps.budgeting.views import (
    BudgetActualViewSet,
    BudgetLineViewSet,
    BudgetViewSet,
    CostCenterViewSet,
)

router = DefaultRouter()
router.register("cost-centers", CostCenterViewSet, basename="cost-centers")
router.register("budgets", BudgetViewSet, basename="budgets")
router.register("budget-lines", BudgetLineViewSet, basename="budget-lines")
router.register("actuals", BudgetActualViewSet, basename="budget-actuals")

urlpatterns = router.urls
