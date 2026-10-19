from rest_framework.routers import DefaultRouter

from apps.specifications.views import (
    SpecificationItemViewSet,
    SpecificationTemplateViewSet,
    SpecificationValueViewSet,
)

router = DefaultRouter()
router.register("specification-templates", SpecificationTemplateViewSet, basename="specificationtemplate")
router.register("specification-items", SpecificationItemViewSet, basename="specificationitem")
router.register("specification-values", SpecificationValueViewSet, basename="specificationvalue"

urlpatterns = router.urls
