from django.contrib import admin

from apps.uom.models import Uom, UomConversion


@admin.register(Uom)
class UomAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "dimension", "is_active")
    list_filter = ("dimension", "is_active")
    search_fields = ("code", "name")
    readonly_fields = ("code",)


@admin.register(UomConversion)
class UomConversionAdmin(admin.ModelAdmin):
    list_display = ("from_uom", "to_uom", "factor", "is_active")
    list_filter = ("is_active",)
    search_fields = ("from_uom__code", "to_uom__code")
