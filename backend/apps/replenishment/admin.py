from django.contrib import admin

from apps.replenishment.models import (
    ReplenishmentLine,
    ReplenishmentOrder,
    ReplenishmentPolicy,
    ReplenishmentRun,
)

admin.site.register(ReplenishmentPolicy)
admin.site.register(ReplenishmentPolicy)
admin.site.register(ReplenishmentLine)
admin.site.register(ReplenishmentOrder)
