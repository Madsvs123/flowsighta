from rest_framework.routers import DefaultRouter

from apps.sales_orders.views import (
    OrderAllocationViewSet,
    SalesOrderLineViewSet,
    SalesOrderViewSet,
    SalesShipmentViewSet,
)

router = DefaultRouter()
router.register("sales-orders", SalesOrderViewSet, basename="sales-orders")
router.register("sales-order-lines", SalesOrderLineViewSet, basename="sales-order-lines")
router.register("order-allocations", OrderAllocationViewSet, basename="order-allocations")
router.register("shipments", SalesShipmentViewSet, basename="sales-shipments")

urlpatterns = router.urls
