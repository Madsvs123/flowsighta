from django.contrib import admin

from apps.portfolios.models import CapitalRequest, Portfolio, PortfolioProject, PortfolioReview


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")
    search_fields = ("name",)


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "project_ref", "weight")
    list_filter = ("portfolio",)
    search_fields = ("project_ref",)


@admin.register(PortfolioReview)
class PortfolioReviewAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "date", "reviewed_by")
    list_filter = ("date",)


@admin.register(CapitalRequest)
class CapitalRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "portfolio", "amount", "status", "submitted_by")
    list_filter = ("status",)
    search_fields = ("title", "portfolio__description")
