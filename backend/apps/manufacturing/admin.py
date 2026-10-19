from django.contrib import admin

from apps.manufacturing.models import MaterialIssue, ProductionOrder, ProductionOutput, ProductionStep


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "product", "quantity", "status", "priority")
    list_filter = ("status", "priority")
    search_fields = ("number", "product__sku", "product__name")


@admin.register(ProductionStep)
class ProductionStepAdmin(admin.ModelAdmin):
    list_display = ("order", "sequence", "operation", "status")
    list_filter = ("status",)


@admin.register(ProductionOutput)
class ProductionOutputAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "batch_number", "produced_at")
    search_fields = ("batch_number",)


@admin.register(MaterialIssue)
class MaterialIssueAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "from_bin", "issued_at", "issued_by")
