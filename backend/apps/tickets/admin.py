from django.contrib import admin

from apps.tickets.models import SupportTicket, TicketCategory, TicketMessage, TicketSla

admin.site.register(TicketCategory)
admin.site.register(SupportTicket)
admin.site.register(TicketMessage)
admin.site.register(TicketSla)
