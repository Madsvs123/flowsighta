from rest_framework.routers import DefaultRouter

from apps.warranty.views import (
    ClaimResolutionViewSet,
    WarrantyClaimViewSet,
    WarrantyPlanViewSet,
    WarrantyRegistrationViewSet,
)

router = DefaultRouter()
router.register("warranty-plans", WarrantyPlanViewSet, basename="warranty-plans")
router.register("registrations", WarrantyRegistrationViewSet, basename="warranty-registrations")
router.register("claims", WarrantyClaimViewSet, basename="warranty-claims")
router.register("resolutions", ClaimResolutionViewSet, basename="claim-resolutions")

urlpatterns = router.urls
