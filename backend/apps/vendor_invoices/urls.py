from rest_framework.routers import DefaultRouter

from apps.vendor_invoices.views import (
    InvoiceApprovalViewSet,
    InvoiceMatchViewSet,
    VendorInvoiceLineViewSet,
    VendorInvoiceViewSet,
)

router = DefaultRouter()
router.register("vendor-invoices", VendorInvoiceViewSet, basename="vendor-invoices"
router.register("vendor-invoice-lines", VendorInvoiceLineViewSet, basename="vendor-invoice-line")
router.register("invoice-matches", InvoiceMatchViewSet, basename="invoice-matches")
router.register("invoice-approvals", InvoiceApprovalViewSet, basename="invoice-approvals")

urlpatterns = router.urls
