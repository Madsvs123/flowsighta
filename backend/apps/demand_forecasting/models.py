from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Forecast(TenantModel, AuditedModel):
    class Method(models.TextChoices):
        NAIVE = "naive", "Naive"
        MOVING_AVERAGE = "moving_average", "Moving Average"
        EXPONENTIAL = "exponential", "Exponential Smoothing"
        SEASONAL = "seasonal", "Seasonal"
        ML = "ml", "Machine Learning"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="forecasts"
    )
    horizon_days = models.PositiveIntegerField(default=90)
    method = models.CharField(
        max_length=32, choices=Method.choices, default=Method.MOVING_AVERAGE
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "product", "status"])]

    def __str__(self):
        return f"Forecast {self.product.sku} ({self.method})"


class ForecastLine(TenantModel):
    forecast = models.ForeignKey(Forecast, on_delete=models.CASCADE, related_name="lines")
    period = models.DateField()
    quantity = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    confidence = models.PositiveIntegerField(default=80)

    class Meta:
        ordering = ["period"]
        unique_together = ("organization", "forecast", "period")

    def __str__(self):
        return f"{self.forecast_id} @ {self.period}: {self.quantity}"


class ForecastAdjustment(TenantModel):
    line = models.ForeignKey(ForecastLine, on_delete=models.CASCADE, related_name="adjustments")
    adjusted_quantity = models.DecimalField(max_digits=14, decimal_places=3)
    reason = models.CharField(max_length=200, blank=True)
    adjusted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="forecast_adjustments",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Adjustment {self.adjusted_quantity} on line {self.line_id}"


class ForecastAccuracy(TenantModel):
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="forecast_accuracy_records"
    )
    period = models.DateField()
    forecast_qty = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    actual_qty = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    error_pct = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ["-period"]
        unique_together = ("organization", "product", "period")

    def __str__(self):
        return f"{self.product.sku} {self.period}: {self.error_pct}%"
