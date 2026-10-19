from django.contrib import admin

from apps.demand_forecasting.models import (
    Forecast,
    ForecastAccuracy,
    ForecastAdjustment,
    ForecastLine,
)

admin.site.register(Forecast)
admin.site.register(ForecastLine)
admin.site.register(ForecastLine)
admin.site.register(ForecastAccuracy)
