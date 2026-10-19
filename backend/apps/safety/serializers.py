from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.safety.models import Incident, IncidentInvestigation, SafetyInspection, SafetyTraining


class IncidentSerializer(TenantSerializer):
    class Meta:
        model = Incident
        fields = (
            "id",
            "number",
            "date",
            "type",
            "severity",
            "location",
            "description",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class IncidentInvestigationSerializer(TenantSerializer):
    incident_number = serializers.CharField(source="incident.number", read_only=True)

    class Meta:
        model = IncidentInvestigation
        fields = (
            "id",
            "incident",
            "incident_number",
            "findings",
            "root_cause",
            "corrective_actions",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SafetyInspectionSerializer(TenantSerializer):
    inspector_name = serializers.CharField(source="inspector.get_username", read_only=True)

    class Meta:
        model = SafetyInspection
        fields = (
            "id",
            "location",
            "date",
            "inspector",
            "inspector_name",
            "findings",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SafetyTrainingSerializer(TenantSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)

    class Meta:
        model = SafetyTraining
        fields = (
            "id",
            "employee",
            "employee_name",
            "topic",
            "date",
            "expiry_date",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
