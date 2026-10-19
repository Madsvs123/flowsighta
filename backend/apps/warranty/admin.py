from django.contrib import admin

from apps.warranty.models import (
    ClaimResolution,
    WarrantyClaim,
    WarrantyPlan,
    WarrantyRegistration,
)

admin.site.register(WarrantyPlans)
admin.site.register(WarrantyRegistration)
admin.site.register(WarrantyClaim)
admin.site.register(ClaimResolution)
