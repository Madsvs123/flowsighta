from rest_framework.routers import SimpleRouter

from apps.portfolios.views import (
    CapitalRequestViewSet,
    PortfolioProjectViewSet,
    PortfolioReviewViewSet,
    PortfolioViewSet,
)

router = SimpleRouter()
router.register("portfolios", PortfolioViewSet, basename="portfolio")
router.register("portfolio-projects", PortfolioProjectViewSet, basename="portfolioproject")
router.register("portfolio-reviews", PortfolioReviewViewSet, basename="portfolioreview")
router.register("capital-requests", CapitalRequestViewSet, basename="capitalrequest")

urlpatterns = router.urls
