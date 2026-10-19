from django.contrib import admin

from apps.taxation.models import TaxCode, TaxRate, TaxRule


@admin.register(TaxCode)
class TaxCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ("tax_code", "jurisdiction", "rate", "is_active", "effective_from", "effective_to")
    list_filter = ("is_active", "jurisdiction")
    search_fields = ("jurisdiction", "tax_code__rate")


@admin.register(TaxRule)
class TaxRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "product", "tax_code")
    search_fields = ("name", "category")
