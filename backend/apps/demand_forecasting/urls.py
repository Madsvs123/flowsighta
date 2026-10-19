from rest_framework.routers import DefaultRouter

from apps.demand_forecasting.views import (
    ForecastAccuracyViewSet,
    ForecastAdjustmentViewSet,
    ForecastLineViewSet,
    ForecastViewSet,
)

router = DefaultRouter()
router.register("demand-forecasting/forecasts", ForecastViewSet, basename="forecast")
router.register("demand-forecasting/forecast-lines", ForecastLineViewSet, basename="forecast-line")
router.register("demand-forecasting/forecast-adjustments", ForecastLineViewSet, basename="forecast-adjustment")
router.register("demand-forecasting/forecast-accuracy", ForecastAccuracyViewSet, basename="forecast-accuracy")

urlpatterns = router.urls
