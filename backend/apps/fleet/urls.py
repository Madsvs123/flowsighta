from rest_framework.routers import DefaultRouter

from apps.fleet.views import (
    DriverViewSet,
    FuelLogViewSet,
    VehicleMaintenanceViewSet,
    VehicleViewSet,
)

router = DefaultRouter()
router.register("fleet", VehicleViewSet, basename="fleet")
router.register("fleet-drivers", DriverViewSet, basename="fleet-drivers")
router.register("fleet-maintenance", VehicleMaintenanceViewSet, basename="fleet-maintenances")
router.register("fleet-fuel", FuelLogViewSet, basename="fleet-fuel")

urlpatterns = router.urls
