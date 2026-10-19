from django.contrib import admin

from apps.subscriptions.models import Renewal, Subscription, SubscriptionInvoice, SubscriptionLine


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("plan", "customer_ref", "status", "billing_cycle", "start_date", "next_billing_date")
    list_filter = ("status", "billing_cycle")
    search_fields = ("plan", "customer_ref")


@admin.register(SubscriptionLine)
class SubscriptionLineAdmin(admin.ModelAdmin):
    list_display = ("subscription", "product", "quantity")
    search_fields = ("subscription__plan", "product__sku")


@admin.register(SubscriptionInvoice)
class SubscriptionInvoiceAdmin(admin.ModelAdmin):
    list_display = ("subscription", "period_start", "period_end", "amount", "status")
    list_filter = ("status",)
    search_fields = ("subscription__plan", "subscription__customer_ref")


@admin.register(Renewal)
class RenewalAdmin(admin.ModelAdmin):
    list_display = ("subscription", "renewal_date", "status", "amount")
    list_filter = ("status",)
