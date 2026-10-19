from django.db import models

from apps.core.models import AuditedModel, TenantModel


class PerformanceScorecard(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    supplier = models.ForeignKey(
        "suppliers.Supplier", on_delete=models.CASCADE, related_name="performance_scorecards"
    )
    period = models.CharField(max_length=20, db_index=True)
    on_time_delivery_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fill_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    quality_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    cost_index = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    composite_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)

    class Meta:
        ordering = ["-period", "-created_at"]
        unique_together = ("organization", "supplier", "period")
        indexes = [models.Index(fields=["organization", "supplier", "status"])]

    def __str__(self):
        return f"{self.supplier.name} · {self.period}"

    def compute_composite(self):
        weights = {
            m.metric: float(m.weight or 0)
            for m in self.metrics.all()
            if m.metric == "composite"
        }
        values = {
            "otd": float(self.on_time_delivery_rate or 0),
            "fill": float(self.fill_rate or 0),
            "quality": float(self.quality_rate or 0),
            "cost": float(self.cost_index or 0),
        }
        total_weight = sum(weights.values()) or 1
        return round(
            sum(values.get(k, 0) * w for k, w in weights.items()) / total_weight, 2
        )


class ScorecardMetric(TenantModel):
    class Metric(models.TextChoices):
        OTD = "otd", "On-Time Delivery"
        FILL = "fill", "Fill Rate"
        QUALITY = "quality", "Quality"
        COST = "cost", "Cost Index"
        COMPOSITE = "composite", "Composite"

    scorecard = models.ForeignKey(
        PerformanceScorecard, on_delete=models.CASCADE, related_name="metrics"
    )
    metric = models.CharField(max_length=20, choices=Metric.choices)
    target = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    actual = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        ordering = ["metric"]
        unique_together = ("organization", "scorecard", "metric")

    def __str__(self):
        return f"{self.scorecard} · {self.metric}"
