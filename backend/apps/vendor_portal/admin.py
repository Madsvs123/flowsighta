from django.contrib import admin

from apps.vendor_portal.models import PortalDocument, PortalMessage, PortalUser


@admin.register(PortalUser)
class PortalUserAdmin(admin.ModelAdmin):
    list_display = ("supplier", "user", "role", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("supplier__name", "user__email")


@admin.register(PortalDocument)
class PortalDocumentAdmin(admin.ModelAdmin):
    list_display = ("supplier", "title", "type", "status", "created_at")
    list_filter = ("type", "status")
    search_fields = ("title", "supplier__name")


@admin.register(PortalMessage)
class PortalMessageAdmin(admin.ModelAdmin):
    list_display = ("supplier", "subject", "direction", "is_read", "created_at")
    list_filter = ("direction", "is_read")
    search_fields = ("subject", "supplier__name")
