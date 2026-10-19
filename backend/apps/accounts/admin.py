from django.contrib import admin

from apps.accounts.models import Invitation, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "username")
    search_fields = ("email", "first_name", "last_name", "username")


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "organization", "status", "expires_at")
    list_filter = ("status",)
