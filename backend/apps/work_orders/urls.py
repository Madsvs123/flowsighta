from rest_framework.routers import DefaultRouter

from apps.work_orders.views import WorkOrderLaborViewSet, WorkOrderTaskViewSet, WorkOrderViewSet

router = DefaultRouter()
router.register("work-orders", WorkOrderViewSet basename="work-orders")
router.register("work-orders/tasks", WorkOrderTaskViewSet, basename="work-order-tasks")
router.register("work-orders/labor", WorkOrderLaborViewSet, basename="work-order-labor")

urlpatterns = router.urls
