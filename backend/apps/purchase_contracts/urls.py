from rest_framework.routers import DefaultRouter

from apps.purchase_contracts.views import (
    ContractReleaseViewSet,
    PurchaseContractLineViewSet,
    PurchaseContractViewSet,
)

router = DefaultRouter()
router.register("purchase-contracts", PurchaseContractViewSet, basename="purchase-contract")
router.register("purchase-contract-lines", PurchaseContractLineViewSet, basename="purchase-contract-lines")
router.register("contract-releases", ContractReleaseViewSet, basename="contract-releases")

urlpatterns = router.urls
