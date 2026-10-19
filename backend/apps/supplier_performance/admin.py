from django.contrib import admin

from apps.supplier_performance.models import PerformanceScorecard, ScorecardMetric


@admin.register(PerformanceScorecard)
class PerformanceScorecardAdmin(admin.ModelAdmin):
    list_display = (
        "supplier",
        "period",
        "on_time_delivery_rate",
        "fill_rate",
        "quality_rate",
        "cost_index",
        "composite_score",
        "status",
    )
    list_filter = ("status", "period")
    search_fields = ("supplier__name", "period")


@admin.register(ScorecardMetric)
class ScorecardMetricAdmin(admin.ModelAdmin):
    list_display = ("scorecard", "metric", "target", "actual", "weight")
    list_filter = ("metric",)
    search_fields = ("scorecard__supplier__name", "period")
