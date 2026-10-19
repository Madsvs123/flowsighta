from django.db import models

from apps.core.models import AuditedModel, TenantModel


class PlanningConfig(TenantModel):
    horizon_weeks = models.PositiveIntegerField(default=12)
    bucket = models.CharField(max_length=20, default="weekly")
    service_level_target = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    default_safety_stock_days = models.PositiveIntegerField(default=7)
    auto_create_requisitions = models.BooleanField(default=False)
    frozen_horizon_days = models.PositiveIntegerField(default=14)


class DemandForecast(TenantModel, AuditedModel):
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE, related_name="forecasts")
    warehouse = models.ForeignKey(
        "organizations.Warehouse", null=True, blank=True, on_delete=models.SET_NULL, related_name="forecasts"
    )
    period_start = models.DateField()
    period_end = models.DateField()
    forecast_qty = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    actual_qty = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    method = models.CharField(max_length=40, default="moving_average")
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "product", "warehouse", "period_start")
        ordering = ["-period_start"]


class HistoricalDemand(TenantModel):
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE, related_name="historical_demand")
    warehouse = models.ForeignKey(
        "organizations.Warehouse", null=True, blank=True, on_delete=models.SET_NULL, related_name="historical_demand"
    )
    period_start = models.DateField()
    period_end = models.DateField()
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    source = models.CharField(max_length=40, default="sales")

    class Meta:
        unique_together = ("organization", "product", "warehouse", "period_start")


class InventoryProjection(TenantModel):
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE, related_name="projections")
    warehouse = models.ForeignKey("organizations.Warehouse", on_delete=models.CASCADE, related_name="projections")
    as_of = models.DateField()
    starting_on_hand = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    incoming = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    forecast_demand = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    projected_on_hand = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    stockout_risk = models.CharField(max_length=20, default="low")

    class Meta:
        unique_together = ("organization", "product", "warehouse", "as_of")
        ordering = ["as_of"]


class ReplenishmentRecommendation(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        CONVERTED = "converted", "Converted"

    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE, related_name="replenishments")
    warehouse = models.ForeignKey("organizations.Warehouse", on_delete=models.CASCADE, related_name="replenishments")
    supplier = models.ForeignKey(
        "suppliers.Supplier", null=True, blank=True, on_delete=models.SET_NULL, related_name="replenishments"
    )
    recommended_qty = models.DecimalField(max_digits=14, decimal_places=0)
    reason = models.CharField(max_length=200, blank=True)
    needed_by = models.DateField(null=True, blank=True)
    projected_stockout_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=20, default="medium")
    estimated_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)


class PurchaseRequirement(TenantModel):
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE, related_name="purchase_requirements")
    warehouse = models.ForeignKey("organizations.Warehouse", on_delete=models.CASCADE, related_name="purchase_requirements")
    period_start = models.DateField()
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    supplier = models.ForeignKey(
        "suppliers.Supplier", null=True, blank=True, on_delete=models.SET_NULL, related_name="purchase_requirements"
    )
    status = models.CharField(max_length=20, default="planned")
