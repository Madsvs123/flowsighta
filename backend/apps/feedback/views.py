from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.feedback.models import Complaint, FeedbackResponse, FeedbackSurvey, NpsScore
from apps.feedback.serializers import (
    ComplaintSerializer,
    FeedbackResponseSerializer,
    FeedbackSurveySerializer,
    NpsScoreSerializer,
)


class FeedbackSurveyViewSet(TenantViewSet):
    queryset = FeedbackSurvey.objects.prefetch_related("responses", "nps_scores")
    serializer_class = FeedbackSurveySerializer
    required_permission = "feedback.view"
    write_permission = "feedback.manage"
    search_fields = ["title"]
    filterset_fields = ["status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        scores = list(
            NpsScore.objects.filter(organization=request.organization).values_list("score", flat=True)
        )
        nps = None
        if scores:
            promoters = sum(1 for s in scores if s >= 9)
            detractors = sum(1 for s in scores if s <= 6)
            nps = round((promoters - detractors) / len(scores) * 100)
        complaints = Complaint.objects.filter(organization=request.organization)
        return Response(
            {
                "surveys": qs.count(),
                "draft": qs.filter(status=FeedbackSurvey.Status.DRAFT).count(),
                "active": qs.filter(status=FeedbackSurvey.Status.ACTIVE).count(),
                "closed": qs.filter(status=FeedbackSurvey.Status.CLOSED).count(),
                "responses": FeedbackResponse.objects.filter(
                    organization=request.organization
                ).count(),
                "nps_scores": len(scores),
                "nps": nps,
                "complaints": complaints.count(),
                "open_complaints": complaints.filter(
                    status__in=[Complaint.Status.OPEN, Complaint.Status.INVESTIGATING]
                ).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None)
        survey = self.get_object()
        if survey.status != FeedbackSurvey.Status.DRAFT:
            raise ValidationError("Only draft surveys can be activated.")
        survey.status = FeedbackSurvey.Status.ACTIVE
        survey.updated_by = request.user
        survey.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(survey).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        survey = self.get_object()
        if survey.status != FeedbackSurvey.Status.ACTIVE:
            raise ValidationError("Only active surveys can be closed.")
        survey.status = FeedbackSurvey.Status.CLOSED
        survey.updated_by = request.user
        survey.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(survey).data)


class FeedbackResponseViewSet(TenantViewSet):
    queryset = FeedbackResponse.objects.select_related("survey")
    serializer_class = FeedbackResponseSerializer
    required_permission = "feedback.view"
    write_permission = "feedback.manage"
    search_fields = ["respondent_ref", "survey__title"]
    filterset_fields = ["survey"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            submitted_at=timezone.now(),
        )


class NpsScoreViewSet(TenantViewSet):
    queryset = NpsScore.objects.select_related("survey")
    serializer_class = NpsScoreSerializer
    required_permission = "feedback.view"
    write_permission = "feedback.manage"
    search_fields = ["comment", "survey__title"]
    filterset_fields = ["survey", "score"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            submitted_at=timezone.now(),
        )


class ComplaintViewSet(TenantViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    required_permission = "feedback.view"
    write_permission = "feedback.manage"
    search_fields = ["customer_ref", "subject", "description"]
    filterset_fields = ["status", "customer_ref"]

    @action(detail=True, methods=["post"])
    def investigate(self, request, pk=None):
        complaint = self.get_object()
        if complaint.status != Complaint.Status.OPEN:
            raise ValidationError("Only open complaints can be investigated.")
        complaint.status = Complaint.Status.INVESTIGATING
        complaint.updated_by = request.user
        complaint.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(complaint).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        complaint = self.get_object()
        if complaint.status not in (
            Complaint.Status.OPEN,
            Complaint.Status.INVESTIGATING,
        ):
            raise ValidationError("Only open or investigating complaints can be resolved.")
        complaint.status = Complaint.Status.RESOLVED
        complaint.resolution = request.data.get("resolution", "Resolved")
        complaint.updated_by = request.user
        complaint.save(update_fields=["status", "resolution", "updated_at", "updated_by"])
        return Response(self.get_serializer(complaint).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        complaint = self.get_object()
        if complaint.status != Complaint.Status.CLOSED:
            raise ValidationError("Only resolved complaints can be closed.")
        complaint.status = Complaint.Status.CLOSED
        complaint.updated_by = request.user
        complaint.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(complaint).data)
