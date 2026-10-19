from django.contrib import admin

from apps.fleet.models import Driver, FuelLog, Vehicle, VehicleMaintenance

admin.site.register(Vehicle)
admin.site.register(Driver)
admin.site.register(VehicleMaintenance)
admin.site.register(FuelLog)
