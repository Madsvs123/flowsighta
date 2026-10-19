from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.risk.models import RiskAssessment, RiskMitigation, RiskRegister, RiskReview


class RiskRegisterSerializer(TenantSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)

    class Meta:
        model = RiskRegister
        fields = (
            "id",
            "name",
            "category",
            "description",
            "owner",
            "owner_name",
            "impact",
            "likelihood",
            "score",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class RiskAssessmentSerializer(TenantSerializer):
    risk_name = serializers.CharField(source="risk.name", read_only=True)
    assessor_name = serializers.CharField(source="assessor.get_full_name", read_only=True)

    class Meta:
        model = RiskAssessment
        fields = (
            "id",
            "risk",
            "risk_name",
            "date",
            "assessor",
            "assessor_name",
            "impact",
            "likelihood",
            "score",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class RiskMitigationSerializer(TenantSerializer):
    risk_name = serializers.CharField(source="risk.name", read_only=True)
    owner_name = serializers.CharField(source="owner.get_fullname", read_only=True)

    class Meta:
        model = RiskMitigation
        fields = (
            "id",
            "risk",
            "risk_name",
            "action",
            "owner",
            "owner_name",
            "due_date",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class RiskReviewSerializer(TenantSerializer):
    risk_name = serializers.CharField(source="risk.name", read_only=True)
    reviewer_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)

    class Meta:
        model = RiskReview
        fields = (
            "id",
            "risk",
            "risk_name",
            "date",
            "notes",
            "reviewed_by",
            "reviewer_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
