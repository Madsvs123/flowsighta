from rest_framework.routers import DefaultRouter

from apps.invoicing.views import CreditNoteViewSet, CustomerInvoiceViewSet, InvoiceLineViewSet

router = DefaultRouter()
router.register("invoices", CustomerInvoiceViewSet, basename="invoices")
router.register("invoice-lines", CustomerInvoiceViewSet, basename="invoice-lines")
router.register("credit-notes", CreditNoteViewSet, basename="credit-notes")

urlpatterns = router.urls
