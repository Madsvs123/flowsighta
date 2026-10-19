from rest_framework.routers import DefaultRouter

from apps.procurement.views import (
    ApprovalStepViewSet,
    BackorderViewSet,
    GoodsReceiptViewSet,
    PurchaseOrderLineViewSet,
    PurchaseOrderViewSet,
    RequisitionLineViewSet,
    RequisitionViewSet,
)

router = DefaultRouter()
router.register("requisitions", RequisitionViewSet, basename="requisition")
router.register("requisition-lines", RequisitionLineViewSet, basename="requisition-lines")
router.register("approvals", ApprovalStepViewSet, basename="approvals")
router.register("purchase-orders", PurchaseOrderViewSet, basename="purchase-orders")
router.register("purchase-order-lines", PurchaseOrderLineViewSet, basename="purchase-order-lines")
router.register("goods-receipts", GoodsReceiptViewSet, basename="goods-receipts")
router.register("backorders", BackorderViewSet, basename="backorder")

urlpatterns = router.urls
