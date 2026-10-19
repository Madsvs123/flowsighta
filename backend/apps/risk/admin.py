from django.contrib import admin

from apps.risk.models import RiskAssessment, RiskMitigation, RiskRegister, RiskReview


@admin.register(RiskRegister)
class RiskRegisterAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "impact", "likelihood", "score", "status", "owner")
    list_filter = ("status", "impact", "likelihood", "category")
    search_fields = ("name", "category", "description")


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ("risk", "date", "impact", "likelihood", "score", "assessor")
    list_filter = ("impact", "likelihood")


@admin.register(RiskMitigation)
class RiskMitigationAdmin(admin.ModelAdmin):
    list_display = ("action", "risk", "owner", "due_date", "status")
    list_filter = ("status",)
    search_fields = ("action", "risk__name")


@admin.register(RiskReview)
class RiskReviewAdmin(admin.ModelAdmin):
    list_display = ("risk", "date", "reviewed_by", "reviewer")
    list_filter = ("date",)
