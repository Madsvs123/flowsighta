from rest_framework.routers import DefaultRouter

from apps.taxation.views import TaxCodeViewSet, TaxRateViewSet, TaxRuleViewSet

router = DefaultRouter()
router.register("tax-codes", TaxCodeViewSet, basename="tax-code")
router.register("tax-rates", TaxRateViewSet, basename="taxrate")
router.register("tax-rules", TaxRuleViewSet, basename="taxrule")

urlpatterns = router.urls
