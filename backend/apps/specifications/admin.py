from django.contrib import admin

from apps.specifications.models import (
    SpecificationItem,
    SpecificationTemplate,
    SpecificationValue,
)


@admin.register(SpecificationTemplate)
class SpecificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)


@admin.register(SpecificationItem)
class SpecificationItemAdmin(admin.ModelAdmin):
    list_display = ("name", "template", "field_type", "options")
    list_filter = ("field_type", "required")
    search_fields = ("name", "template__name")


@admin.register(SpecificationValue)
class SpecificationValueAdmin(admin.ModelAdmin):
    list_display = ("item", "product", "value")
    search_fields = ("value", "product__sku", "item__name")
