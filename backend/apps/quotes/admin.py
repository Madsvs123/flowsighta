from django.contrib import admin

from apps.quotes.models import QuoteConversion, QuoteLine, QuoteRevision, SalesQuote


@admin.register(SalesQuote)
class SalesQuoteAdmin(admin.ModelAdmin):
    list_display = ("number", "customer_ref", "status", "total", "currency", "valid_until")
    list_filter = ("status", "currency")
    search_fields = ("number", "customer_ref")


@admin.register(QuoteLine)
class QuoteLineAdmin(admin.ModelAdmin):
    list_display = ("quote", "product", "quantity", "unit_price", "line_total")
    search_fields = ("quote__number", "product__sku")


@admin.register(QuoteRevision)
class QuoteRevisionAdmin(admin.ModelAdmin):
    list_display = ("quote", "version", "total", "revised_by_name")
    search_fields = ("quote__number",)


@admin.register(QuoteConversion)
class QuoteConversionAdmin(admin.ModelAdmin):
    list_display = ("quote", "sales_order_ref", "converted_at")
    search_fields = ("quote__number", "sales_order_ref")
