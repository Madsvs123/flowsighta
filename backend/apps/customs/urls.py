from rest_framework.routers import DefaultRouter

from apps.customs.views import (
    ComplianceRuleViewSet,
    CustomsDeclarationViewSet,
    CustomsDocumentViewSet,
    HsCodeViewSet,
)

router = DefaultRouter()
router.register("customs", CustomsDeclarationViewSet, basename="customs")
router.register("customs-hs-codes", HsCodeViewSet, basename="customs-hs-codes")
router.register("customs-document", CustomsDocumentViewSet, basename="customs-documents")
router.register("customs-rules", ComplianceRuleViewSet, basename="customs-rules")

urlpatterns = router.urls
