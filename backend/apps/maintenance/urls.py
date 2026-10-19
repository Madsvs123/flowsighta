from rest_framework.routers import DefaultRouter

from apps.maintenance.views import (
    EquipmentViewSet,
    MaintenanceLogViewSet,
    MaintenanceOrderViewSet,
    MaintenancePlanViewSet,
)

router = DefaultRouter()
router.register("maintenance/equipment", EquipmentViewSet, basename="equipment")
router.register("maintenance/plans", MaintenancePlanViewSet, basename="maintenance-plans")
router.register("maintenance/order", MaintenanceOrderViewSet, basename="maintenance-orders")
router.register("maintenance/logs", MaintenanceLogViewSet, basename="maintenance-logs")

urlpatterns = router.urls
