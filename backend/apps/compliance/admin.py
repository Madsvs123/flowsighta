from django.contrib import admin

from apps.compliance.models import (
    ComplianceAssessment,
    ComplianceCertificate,
    ComplianceRequirement,
    RegulatoryUpdate,
)


@admin.register(ComplianceRequirement)
class ComplianceRequirementAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "applies_to")
    list_filter = ("category",)
    search_fields = ("name", "category")


@admin.register(ComplianceCertificate)
class ComplianceCertificateAdmin(admin.ModelAdmin):
    list_display = ("number", "supplier", "requirement", "expires_date", "status")
    list_filter = ("status",)
    search_fields = ("number", "supplier__name", "requirement__title")


@admin.register(ComplianceAssessment)
class ComplianceAssessmentAdmin(admin.ModelAdmin):
    list_display = ("certificate", "date", "result", "assessor")
    list_filter = ("result",)


@admin.register(RegulatoryUpdate)
class RegulatoryUpdateAdmin(admin.ModelAdmin):
    list_display = ("title", "region", "effective_date", "status")
    list_filter = ("region", "status")
    search_fields = ("title", "region")
