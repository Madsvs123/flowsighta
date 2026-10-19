from django.contrib import admin

from apps.safety.models import Incident, IncidentInvestigation, SafetyInspection, SafetyTraining


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("number", "date", "type", "severity", "location", "status")
    list_filter = ("type", "status")
    search_fields = ("number", "location", "description")


@admin.register(IncidentInvestigation)
class IncidentInvestigationAdmin(admin.ModelAdmin):
    list_display = ("incident", "status")
    list_filter = ("status",)


@admin.register(SafetyInspection)
class SafetyInspectionAdmin(admin.ModelAdmin):
    list_display = ("location", "date", "inspector", "status")
    list_filter = ("status",)
    search_fields = ("location",)


@admin.register(SafetyTraining)
class SafetyTrainingAdmin(admin.ModelAdmin):
    list_display = ("employee", "topic", "date", "expiry_date")
    list_filter = ("topic",)
    search_fields = ("topic", "employee__email")
