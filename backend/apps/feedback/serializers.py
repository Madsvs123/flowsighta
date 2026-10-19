from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.feedback.models import Complaint, FeedbackResponse, FeedbackSurvey, NpsScore


class FeedbackSurveySerializer(TenantSerializer):
    response_count = serializers.SerializerMethodField()
    nps_score = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackSurvey
        fields = (
            "id",
            "title",
            "status",
            "response_count",
            "nps_score",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_response_count(self, obj):
        return obj.responses.count()

    def get_nps_score(self, obj):
        scores = list(obj.nps_scores.values_list("score", flat=True))
        if not scores:
            return None
        promoters = sum(1 for s in scores if s >= 9)
        detractors = sum(1 for s in scores if s < 6)
        return round((promoters - detractors) / len(scores) * 100)


class FeedbackResponseSerializer(TenantSerializer):
    survey_title = serializers.CharField(source="survey.title", read_only=True)

    class Meta:
        model = FeedbackResponse
        fields = (
            "id",
            "survey",
            "survey_title",
            "respondent_ref",
            "answers",
            "submitted_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class NpsScoreSerializer(TenantSerializer):
    survey_title = serializers.CharField(source="survey.title", read_only=True)

    class Meta:
        model = NpsScore
        fields = (
            "id",
            "survey",
            "survey_title",
            "score",
            "comment",
            "submitted_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ComplaintSerializer(TenantSerializer):
    class Meta:
        model = Complaint
        fields = (
            "id",
            "customer_ref",
            "subject",
            "description",
            "status",
            "resolution",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
