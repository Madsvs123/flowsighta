from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.crm.models import CrmActivity, Lead, Opportunity, Pipeline


class LeadSerializer(TenantSerializer):
    class Meta:
        model = Lead
        fields = (
            "id",
            "name",
            "company",
            "email",
            "phone",
            "source",
            "status",
            "value",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "source")


class OpportunitySerializer(TenantSerializer):
    lead_name = serializers.CharField(source="lead.name", read_only=True)
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)

    class Meta:
        model = Opportunity
        fields = (
            "id",
            "lead",
            "lead_name",
            "name",
            "stage",
            "probability",
            "amount",
            "owner",
            "owner_name",
            "expected_close",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CrmActivitySerializer(TenantSerializer):
    opportunity_name = serializers.CharField(source="opportunity.name", read_only=True)
    lead_name = serializers.CharField(source="lead.name", read_only=True)

    class Meta:
        model = CrmActivity
        fields = (
            "id",
            "opportunity",
            "opportunity_name",
            "lead",
            "lead_name",
            "type",
            "notes",
            "occurred_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PipelineSerializer(TenantSerializer):
    class Meta:
        model = Pipeline
        fields = ("id", "name", "stages", "is_default", "is_active", "created_at")
        read_only_fields = ("id", "created_at")
