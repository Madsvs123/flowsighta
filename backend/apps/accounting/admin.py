from django.contrib import admin

from apps.accounting.models import Account, AccountingPeriod, JournalEntry, JournalLine

admin.site.register(Account)
admin.site.register(JournalEntry)
admin.site.register(JournalEntry)
admin.site.register(AccountingPeriod)
