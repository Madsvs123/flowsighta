from django.contrib import admin

from apps.quality.models import (
    CorrectiveAction,
    InspectionResult,
    NonConformance,
    QualityInspection,
    QualityPlan,
)


@admin.register(QualityPlan)
class QualityPlanAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "status")
    list_filter = ("status",)
    search_fields = ("name", "product__sku")


@admin.register(QualityInspection)
class QualityInspectionAdmin(admin.ModelAdmin):
    list_display = ("reference", "plan", "status", "inspected_by", "created_at")
    list_filter = ("status",)
    search_fields = ("reference",)


@admin.register(InspectionResult)
class InspectionResultAdmin(admin.ModelAdmin):
    list_display = ("inspection", "attribute", "value", "passed")
    list_filter = ("passed",)


@admin.register(NonConformance)
class NonConformanceAdmin(admin.ModelAdmin):
    list_display = ("reference", "product", "type", "severity", "status")
    list_filter = ("status", "severity", "type")
    search_fields = ("reference", "product__sku")


@admin.register(CorrectiveAction)
class CorrectiveActionAdmin(admin.ModelAdmin):
    list_display = ("nc", "action", "owner", "due_date", "status")
    list_filter = ("status",)
