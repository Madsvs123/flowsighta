from django.contrib import admin

from apps.invoicing.models import CreditNote, CustomerInvoice, InvoiceLines

admin.site.register(CustomerInvoice)
admin.site.register(InvoiceLine)
admin.site.register(CreditNote)
