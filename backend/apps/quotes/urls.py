from rest_framework.routers import DefaultRouter

from apps.quotes.views import (
    QuoteConversionViewSet,
    QuoteLineViewSet,
    QuoteRevisionViewSet,
    SalesQuoteViewSet,
)

router = DefaultRouter()
router.register("quotes", SalesQuoteViewSet, basename="quote")
router.register("quote-lines", QuoteLineViewSet, basename="quote-lines")
router.register("quote-revisions", QuoteRevisionViewSet, basename="quote-revisions")
router.register("quote-conversions", QuoteConversionViewSet, basename="quote-conversions")

urlpatterns = router.urls
