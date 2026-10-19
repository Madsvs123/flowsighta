from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.portfolios.models import CapitalRequest, Portfolio, PortfolioProject, PortfolioReview


class PortfolioSerializer(TenantSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)

    class Meta:
        model = Portfolio
        fields = ("id", "name", "description", "owner", "owner_name", "created_at")
        read_only_fields = ("id", "created_at")


class PortfolioProjectSerializer(TenantSerializer):
    portfolio_name = serializers.CharField(source="portfolio.description", read_only=True)

    class Meta:
        model = PortfolioProject
        fields = ("id", "portfolio", "portfolio_name", "project_ref", "weight", "created_at")
        read_only_fields = ("id", "created_at")


class PortfolioReviewSerializer(TenantSerializer):
    portfolio_name = serializers.CharField(source="portfolio.name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)

    class Meta:
        model = PortfolioReview
        fields = (
            "id",
            "portfolio",
            "portfolio_name",
            "date",
            "health",
            "notes",
            "reviewed_by",
            "reviewed_by_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CapitalRequestSerializer(TenantSerializer):
    portfolio_name = serializers.CharField(source="portfolio.name", read_only=True)
    submitted_by_name = serializers.CharField(source="submitted_by.get_full_name", read_only=True)

    class Meta:
        model = CapitalRequest
        fields = (
            "id",
            "portfolio",
            "portfolio_name",
            "title",
            "amount",
            "justification",
            "status",
            "submitted_by",
            "submitted_by_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
