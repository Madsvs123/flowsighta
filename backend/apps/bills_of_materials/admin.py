from django.contrib import admin

from apps.bills_of_materials.models import Bom, BomLine, BomRevision


@admin.register(Bom)
class BomAdmin(admin.ModelAdmin):
    list_display = ("product", "version", "status", "effective_from", "effective_to")
    list_filter = ("status",)
    search_fields = ("product__sku", "product__name", "version")


@admin.register(BomLine)
class BomLineAdmin(admin.ModelAdmin):
    list_display = ("bom", "component", "quantity", "scrap_pct", "unit")
    search_fields = ("component__sku",)


@admin.register(BomRevision)
class BomRevisionAdmin(admin.ModelAdmin):
    list_display = ("bom", "version", "approved_by", "approved_at")
