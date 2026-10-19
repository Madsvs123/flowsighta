from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Portfolio(TenantModel, AuditedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_portfolios",
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "description")

    def __str__(self):
        return self.name


class PortfolioProject(TenantModel):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="projects")
    project_ref = models.CharField(max_length=64)
    weight = models.DecimalField(max_digits=6, decimal_places=3, default=1)

    class Meta:
        ordering = ["portfolio__name"]
        unique_together = ("organization", "portfolio", "project_ref")
        indexes = [models.Index(fields=["organization", "portfolio", "project_ref"])]

    def __str__(self):
        return f"{self.portfolio.name} / {self.project_ref}"


class PortfolioReview(TenantModel, AuditedModel):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="reviews")
    date = models.DateField()
    health = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="portfolio_reviews",
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.portfolio.name} review {self.date}"


class CapitalRequest(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="capital_requests")
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    justification = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="capital_requests",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "portfolio", "status"])]

    def __str__(self):
        return f"{self.portfolio.name} / {self.title}"
