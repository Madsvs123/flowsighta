from django.contrib import admin

from apps.service_orders.models import (
    FieldReport,
    ServiceAppointment,
    ServiceLine,
    ServiceOrder,
)

admin.site.register(ServiceOrder)
admin.site.register(ServiceLine)
admin.site.register(ServiceAppointment)
admin.site.register(FieldReport)
