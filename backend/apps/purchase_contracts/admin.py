from django.contrib import admin

from apps.purchase_contracts.models import ContractRelease, PurchaseContract, PurchaseContractLine


@admin.register(PurchaseContract)
class PurchaseContractAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "supplier", "status", "start_date", "end_date", "total_value")
    list_filter = ("status",)
    search_fields = ("number", "title", "supplier__name")


@admin.register(PurchaseContractLine)
class PurchaseContractLineAdmin(admin.ModelAdmin):
    list_display = ("contract", "product", "price", "quantity", "received_quantity")
    search_fields = ("contract__number", "product__sku")


@admin.register(ContractRelease)
class ContractReleaseAdmin(admin.ModelAdmin):
    list_display = ("number", "contract", "quantity", "stat")
    list_filter = ("status",)
    search_fields = ("number", "contract__number")
