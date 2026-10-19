from django.contrib import admin

from apps.freight.models import AccessorialCharge, FreightBill, FreightBooking, FreightQuote

admin.site.register(FreightQuote)
admin.site.register(FreightBooking)
admin.site.register(FreightBill)
admin.site.register(AccessorialCharge)
