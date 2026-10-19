from celery import shared_task


@shared_task
def generate_forecast_lines(organization_id=None):
    """Backfill weekly forecast lines for draft forecasts that have none yet."""
    from datetime import timedelta

    from django.utils import timezone

    from apps.demand_forecasting.models import Forecast, ForecastLine

    today = timezone.now().date()
    created = 0
    forecasts = Forecast.objects.filter(status=Forecast.Status.DRAFT).select_related("product")
    if organization_id:
        forecasts = forecasts.filter(organization_id=organization_id)
    for forecast in forecasts:
        if ForecastLine.objects.filter(forecast=forecast).exists():
            continue
        # Deterministic baseline with a light seasonal pattern per bucket.
        weeks = max(1, forecast.horizon_days // 30)
        for week in range(weeks):
            period = today + timedelta(weeks=week)
            quantity = 10 + (week % 4) * 5
            confidence = max(50, 92 - week * 3)
            ForecastLine.objects.create(
                organization=forecast.organization,
                forecast=forecast,
                period=period,
                quantity=quantity,
                confidence=confidence,
            )
            created += 1
    return {"lines_created": created}


@shared_task
def compute_forecast_accuracy(organization_id=None):
    """Compute MAPE-style accuracy records from the latest adjustment on each line."""
    from apps.demand_forecasting.models import ForecastAccuracy, ForecastLine

    updated = 0
    lines = ForecastLine.objects.filter(adjustments__isnull=False).distinct().select_related(
        "forecast", "forecast__product"
    )
    if organization_id:
        lines = lines.filter(forecast__organization_id=organization_id)
    for line in lines:
        last = line.adjustments.order_by("-created_at").first()
        forecast_qty = float(line.quantity or 0)
        actual_qty = float(last.adjusted_quantity or 0)
        error_pct = abs(actual_qty - forecast_qty) / forecast_qty * 100 if forecast_qty else 0
        _, was_created = ForecastAccuracy.objects.update_or_create(
            organization=line.forecast.organization,
            product=line.forecast.product,
            period=line.period,
            defaults={
                "forecast_qty": forecast_qty,
                "actual_qty": actual_qty,
                "error_pct": error_pct,
            },
        )
        if was_created:
            updated += 1
    return {"accuracy_records": updated}
