from rest_framework.routers import DefaultRouter

from apps.catalog.views import (
    AttributeValueViewSet,
    AttributeViewSet,
    CategoryViewSet,
    ProductVariantViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="categories")
router.register("attributes", AttributeViewSet, basename="attribute")
router.register("attribute-values", AttributeValueViewSet, basename="attributevalue")
router.register("product-variants", ProductVariantViewSet, basename="productvariant")

urlpatterns = router.urls
