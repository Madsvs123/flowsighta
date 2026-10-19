from django.contrib import admin

from apps.payments.models import Payment, PaymentAllocation, PaymentRun, PaymentTerm

admin.site.register(Payment)
admin.site.register(PaymentTerm)
admin.site.register(PaymentRun)
admin.site.register(PaymentAllocation)
