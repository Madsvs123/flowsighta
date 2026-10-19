from rest_framework.routers import DefaultRouter

from apps.pricing.views import (
    DiscountViewSet,
    PriceChangeViewSet,
    PriceListItemViewSet,
    PriceListViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register("price-lists", PriceListViewSet, basename="pricelist")
router.register("price-list-items", PriceListItemViewSet, basename="pricelistitem")
router.register("discounts", DiscountViewSet, basename="discount")
router.register("price-changes", PriceChangeViewSet, basename="pricechange")

urlpatterns = router.urls
