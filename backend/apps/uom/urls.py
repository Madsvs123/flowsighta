from rest_framework.routers import DefaultRouter

from apps.uom.views import UomConversionViewSet, UomViewSet

router = DefaultRouter()
router.register("uoms", UomViewSet, basename="uoms")
router.register("uom-conversions", UomConversionViewSet, basename="uomconversion")

urlpatterns = router.urls
