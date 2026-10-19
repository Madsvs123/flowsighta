from django.contrib import admin

from apps.catalog.models import Attribute, AttributeValue, Category, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    list_filter = ("type",)


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "product", "value", "price")
    search_fields = ("value", "product__sku")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "unit_price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("sku", "product__sku")
