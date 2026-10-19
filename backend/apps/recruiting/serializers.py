from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.recruiting.models import Application, Candidate, Interview, JobPosting, Offer


class JobPostingSerializer(TenantSerializer):
    application_count = serializers.IntegerField(source="applications.count", read_only=True)

    class Meta:
        model = JobPosting
        fields = (
            "id",
            "title",
            "department",
            "status",
            "openings",
            "salary_range",
            "description",
            "application_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CandidateSerializer(TenantSerializer):
    class Meta:
        model = Candidate
        fields = ("id", "name", "email", "phone", "source", "status", "created_at")
        read_only_fields = ("id", "created_at")


class ApplicationSerializer(TenantSerializer):
    candidate_name = serializers.CharField(source="candidate.name", read_only=True)
    candidate_email = serializers.EmailField(source="candidate.email_address", read_only=True)
    posting_title = serializers.CharField(source="posting.title", read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "posting",
            "posting_title",
            "candidate",
            "candidate_name",
            "candidate_email",
            "status",
            "applied_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class InterviewSerializer(TenantSerializer):
    candidate_name = serializers.CharField(source="application.candidate.name", read_only=True)
    posting_title = serializers.CharField(source="application.posting.title", read_only=True)
    interviewer_name = serializers.CharField(source="interviewer.get_full_name", read_only=True)

    class Meta:
        model = Interview
        fields = (
            "id",
            "application",
            "candidate_name",
            "posting_title",
            "interviewer",
            "interviewer_name",
            "date",
            "score",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class OfferSerializer(TenantSerializer):
    candidate_name = serializers.CharField(source="application.candidate.name", read_only=True)
    posting_title = serializers.CharField(source="application.posting.title", read_only=True)

    class Meta:
        model = Offer
        fields = (
            "id",
            "application",
            "candidate_name",
            "posting_title",
            "salary",
            "status",
            "expires_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
