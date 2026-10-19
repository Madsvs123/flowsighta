from django.db.models import Count, Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.recruiting.models import Application, Candidate, Interview, JobPosting, Offer
from apps.recruiting.serializers import (
    ApplicationSerializer,
    CandidateSerializer,
    InterviewSerializer,
    JobPostingSerializer,
    OfferSerializer,
)


class JobPostingViewSet(TenantViewSet):
    queryset = JobPosting.objects.annotate(application_count=Count("applications"))
    serializer_class = JobPostingSerializer
    required_permission = "recruiting.view"
    write_permission = "recruiting.manage"
    search_fields = ["title", "department", "salary_range"]
    filterset_fields = ["status", "department"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = {label: qs.filter(status=value).count() for value, label in JobPosting.Status.choices}
        total_openings = qs.filter(status=JobPosting.Status.OPEN).aggregate(total=Count("openings"))["total"] or 0
        apps = Application.objects.filter(organization=request.organization)
        app_by_status = {label: apps.filter(status=value).count() for value, label in Application.Status.choices}
        return Response(
            {
                "total_postings": qs.count(),
                "by_status": by_status,
                "open_openings": int(total_openings),
                "applications": apps.count(),
                "application_by_status": app_by_status,
                "candidates": Candidate.objects.filter(organization=request.organization).count(),
                "hired": app_by_status["hired"],
            }
        )

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        posting = self.get_object()
        status = request.data.get("status")
        if status not in JobPosting.Status.values:
            return Response({"detail": f"Invalid status. Choose from {', '.join(JobPosting.Status.values)}"}, status=400)
        posting.status = status
        posting.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(posting).data)


class CandidateViewSet(TenantViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    required_permission = "recruiting.view"
    write_permission = "recruiting.manage"
    search_fields = ["name", "email", "phone", "source"]
    filterset_fields = ["status", "source"]


class ApplicationViewSet(TenantViewSet):
    queryset = Application.objects.select_related("posting", "candidate")
    serializer_class = ApplicationSerializer
    required_permission = "recruiting.view"
    write_permission = "recruiting.manage"
    search_fields = ["candidate__name", "candidate__email", "posting__title"]
    filterset_fields = ["posting", "candidate", "status"]

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        application = self.get_object()
        status = request.data.get("status")
        if status not in Application.Status.values:
            return Response({"detail": f"Invalid status. Choose from {', '.join(Application.Status.values)}"}, status=400)
        application.status = status
        application.save(update_fields=["status", "updated_at"])
        candidate = application.candidate
        mapping = {
            Application.Status.SCREENING: Candidate.Status.SCREENED,
            Application.Status.INTERVIEW: Candidate.Status.INTERVIEWED,
            Application.Status.OFFER: Candidate.Status.OFFERED,
            Application.Status.HIRED: Candidate.Status.HIRED,
            Application.Status.REJECTED: Candidate.Status.REJECTED,
        }
        if status in mapping and candidate.status != mapping[status]:
            candidate.status = mapping[status]
            candidate.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(application).data)


class InterviewViewSet(TenantViewSet):
    queryset = Interview.objects.select_related("application", "application__candidate", "application__posting", "interviewer")
    serializer_class = InterviewSerializer
    required_permission = "recruiting.view"
    write_permission = "recruiting.manage"
    search_fields = ["application__candidate__name", "application__posting__title"]
    filterset_fields = ["application", "interviewer"]


class OfferViewSet(TenantViewSet):
    queryset = Offer.objects.select_related("application", "application__candidate", "application__posting")
    serializer_class = OfferSerializer
    required_permission = "recruiting.view"
    write_permission = "recruiting.manage"
    search_fields = ["application__candidate__name", "application__posting__title"]
    filterset_fields = ["application", "status"]

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        offer = self.get_object()
        if offer.status != Offer.Status.SENT:
            return Response({"detail": "Only draft offers can be sent"}, status=400)
        offer.status = Offer.Status.SENT
        offer.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(offer).data)

    @action(detail=True, methods=["post"])
    def respond(self, request, pk=None):
        offer = self.get_object()
        decision = request.data.get("decision")
        if decision not in (Offer.Status.ACCEPTED, Offer.Status.DECLINED):
            return Response({"detail": "Decision must be 'accepted' or 'declined'"}, status=400)
        if offer.status not in (Offer.Status.SENT, Offer.Status.DRAFT):
            return Response({"detail": "Offer is not open for response"}, status=400)
        offer.status = decision
        offer.save(update_fields=["status", "updated_at"])
        if decision == Offer.Status.ACCEPTED:
            application = offer.application
            application.status = Application.Status.HIRED
            application.save(update_fields=["status", "updated_at"])
            candidate = application.candidate
            candidate.status = Candidate.Status.HIRED
            candidate.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(offer).data)
