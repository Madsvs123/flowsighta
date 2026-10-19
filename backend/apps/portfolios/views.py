from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.portfolios.models import CapitalRequest, Portfolio, PortfolioProject, PortfolioReview
from apps.portfolios.serializers import (
    CapitalRequestSerializer,
    PortfolioProjectSerializer,
    PortfolioReviewSerializer,
    PortfolioSerializer,
)


class PortfolioViewSet(TenantViewSet):
    queryset = Portfolio.objects.select_related("owner")
    serializer_class = PortfolioSerializer
    required_permission = "portfolios.view"
    write_permission = "portfolios.manage"
    search_fields = ["name", "description"]
    filterset_fields = ["owner"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        requests = CapitalRequest.objects.filter(organization=request.organization)
        return Response(
            {
                "portfolio_count": qs.count(),
                "project_links": PortfolioProject.objects.filter(organization=request.organization).count(),
                "review_count": PortfolioReview.objects.filter(organization=request.organization).count(),
                "capital_requests": requests.count(),
                "pending_capital": requests.filter(
                    status__in=[CapitalRequest.Status.DRAFT, CapitalRequest.Status.SUBMITTED]
                ).count(),
                "approved_amount": float(
                    requests.filter(status=CapitalRequest.Status.APPROVED).aggregate(v=Sum("amount"))["v"] or 0
                ),
                "by_status": {s: requests.filter(status=s).count() for s, _ in CapitalRequest.Status.choices},
            }
        )


class PortfolioProjectViewSet(TenantViewSet):
    queryset = PortfolioProject.objects.select_related("portfolio")
    serializer_class = PortfolioProjectSerializer
    required_permission = "portfolios.view"
    write_permission = "portfolios.manage"
    search_fields = ["project_ref", "portfolio__name"]
    filterset_fields = ["portfolio"]


class PortfolioReviewViewSet(TenantViewSet):
    queryset = PortfolioReview.objects.select_related("portfolio", "reviewed_by")
    serializer_class = PortfolioReviewSerializer
    required_permission = "portfolios.view"
    write_permission = "portfolios.manage"
    search_fields = ["portfolio__name", "notes"]
    filterset_fields = ["portfolio", "reviewed_by"]


class CapitalRequestViewSet(TenantViewSet):
    queryset = CapitalRequest.objects.select_related("portfolio", "submitted_by")
    serializer_class = CapitalRequestSerializer
    required_permission = "portfolios.view"
    write_permission = "portfolios.manage"
    search_fields = ["title", "justification", "portfolio__name"]
    filterset_fields = ["portfolio", "status", "submitted_by"]

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        capital_request = self.get_object()
        capital_request.status = CapitalRequest.Status.SUBMITTED
        capital_request.submitted_by = request.user
        capital_request.save(update_fields=["status", "submitted_by", "updated_at"])
        return Response(self.get_serializer(capital_request).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        capital_request = self.get_object()
        capital_request.status = CapitalRequest.Status.SUBMITTED
        capital_request.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(capital_request).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        capital_request = self.get_object()
        capital_request.status = CapitalRequest.Status.REJECTED
        capital_request.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(capital_request).data)
