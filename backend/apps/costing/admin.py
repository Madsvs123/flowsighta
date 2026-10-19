from django.contrib import admin

from apps.costing.models import CostingMethod, CostLayer, CostVariance, InventoryValuation

admin.site.register(CostingMethod)
admin.site.register(CostLayer)
admin.site.register(CostLayer)
admin.site.register(InventoryValuation)
