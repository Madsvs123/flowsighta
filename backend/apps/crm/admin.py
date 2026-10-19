from django.contrib import admin

from apps.crm.models import CrmActivity, Lead, Opportunity, Pipeline


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "email", "phone_number", "source", "status", "value")
    list_filter = ("status", "source")
    search_fields = ("name", "company", "email")


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("name", "lead", "stage", "probability", "amount", "owner", "status")
    list_filter = ("status", "stage")
    search_fields = ("name", "lead__name")


@admin.register(CrmActivity)
class CrmActivityAdmin(admin.ModelAdmin):
    list_display = ("type", "opportunity", "lead", "occurred_at")
    list_filter = ("type",)
    search_fields = ("notes", "opportunity__name", "lead__name")


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default", "is_active")
    list_filter = ("is_default", "is_active")
