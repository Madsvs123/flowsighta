from django.contrib import admin

from apps.vendor_invoices.models import (
    InvoiceApproval,
    InvoiceMatch,
    VendorInvoice,
    VendorInvoiceLine,
)


@admin.register(VendorInvoice)
class VendorInvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "supplier", "invoice_date", "due_date", "total", "status")
    list_filter = ("status",)
    search_fields = ("number", "supplier")


@admin.register(VendorInvoiceLine)
class VendorInvoiceLineAdmin(admin.ModelAdmin):
    list_display = ("invoice", "description", "quantity", "rate", "line_total")
    search_fields = ("invoice__number", "description")


@admin.register(InvoiceMatch)
class InvoiceMatchAdmin(admin.ModelAdmin):
    list_display = ("invoice_line", "reference_type", "reference_id", "matched_qty", "variance")
    list_filter = ("reference_type",)


@admin.register(InvoiceApproval)
class InvoiceApprovalAdmin(admin.ModelAdmin):
    list_display = ("invoice", "approver", "status", "decided_at")
    list_filter = ("status",)
