from rest_framework.routers import DefaultRouter

from apps.returns.views import RestockTaskViewSet, ReturnLineViewSet, ReturnOrderViewSet

router = DefaultRouter()
router.register("returns", ReturnOrderViewSet, basename="return-order")
router.register("return-lines", ReturnLineViewSet, basename="return-lines")
router.register("restock-tasks", RestockTaskViewSet, basename="restock-tasks")

urlpatterns = router.urls
