from django.contrib import admin

from apps.portals.models import Portal, PortalActivity, PortalContent, PortalMember


@admin.register(Portal)
class PortalAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "status", "created_at")
    list_filter = ("type", "status")
    search_fields = ("name",)


@admin.register(PortalMember)
class PortalMemberAdmin(admin.ModelAdmin):
    list_display = ("portal", "user", "role")
    list_filter = ("role",)
    search_fields = ("portal__name", "user__email")


@admin.register(PortalContent)
class PortalContentAdmin(admin.ModelAdmin):
    list_display = ("title", "portal", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "portal__name")


@admin.register(PortalActivity)
class PortalActivityAdmin(admin.ModelAdmin):
    list_display = ("portal", "user", "action", "occurred_at")
    list_filter = ("action",)
    search_fields = ("action", "portal__name", "user__email")
