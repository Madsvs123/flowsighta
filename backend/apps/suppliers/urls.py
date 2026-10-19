from rest_framework.routers import DefaultRouter

from apps.suppliers.views import (
    OnboardingStepViewSet,
    PurchaseHistoryViewSet,
    SupplierCertificationViewSet,
    SupplierContactViewSet,
    SupplierContractViewSet,
    SupplierDocumentViewSet,
    SupplierProductViewSet,
    SupplierScoreSnapshotViewSet,
    SupplierViewSet,
)

router = DefaultRouter()
router.register("suppliers", SupplierViewSet, basename="suppliers")
router.register("supplier-contacts", SupplierContactViewSet, basename="supplier-contact")
router.register("supplier-contracts", SupplierContractViewSet, basename="supplier-contracts")
router.register("supplier-products", SupplierProductViewSet, basename="supplier-products")
router.register("supplier-certifications", SupplierCertificationViewSet, basename="supplier-certifications")
router.register("supplier-documents", SupplierDocumentViewSet, basename="supplier-documents")
router.register("supplier-onboarding-steps", OnboardingStepViewSet, basename="supplier-onboarding")
router.register("supplier-scores", SupplierScoreSnapshotViewSet, basename="supplier-scores")
router.register("purchase-history", PurchaseHistoryViewSet, basename="purchase-histories")

urlpatterns = router.urls
