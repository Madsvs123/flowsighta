from django.contrib import admin

from apps.customers.models import Customer, CustomerAddress, CustomerAgreement, CustomerContact


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "status", "country", "credit_limit", "is_tax_exempt")
    list_filter = ("status", "country", "is_tax_exempt")
    search_fields = ("code", "name")


@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    list_display = ("name", "customer", "email", "phone", "role")
    search_fields = ("name", "email", "customer__name")


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("customer", "type", "is_default")
    list_filter = ("type", "is_default")


@admin.register(CustomerAgreement)
class CustomerAgreementAdmin(admin.ModelAdmin):
    list_display = ("title", "customer", "start_date", "end_date", "discount", "status")
    list_filter = ("status",)
    search_fields = ("title", "customer__name")
