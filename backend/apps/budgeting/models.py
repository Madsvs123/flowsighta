from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class CostCenter(TenantModel, AuditedModel):
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=200)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_cost_centers",
    )
    is_active = models.BooleanField(default=True)

    class Meta
        unique_together = ("organization", "code")
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} · {self.name}"


class Budget(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"
        FROZEN = "frozen", "Frozen"

    name = models.CharField(max_length=200)
    cost_center = models.ForeignKey(
        CostCenter, on_delete=models.CASCADE, related_name="budgets"
    )
    fiscal_year = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["-fiscal_year", "name"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.name} ({self.fiscal_year})"


class BudgetLine(TenantModel):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="lines")
    category = models.CharField(max_length=120)
    planned_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        unique_together = ("organization", "budget", "category")
        ordering = ["category"]

    def __str__(self):
        return f"{self.budget.name} · {self.category}"


class BudgetActual(TenantModel):
    line = models.ForeignKey(BudgetLine, on_delete=models.CASCADE, related_name="actuals")
    period = models.CharField(max_length=16)
    actual_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        unique_together = ("organization", "line", "period")
        ordering = ["period"]

    def __str__(self):
        return f"{self.line.category} · {self.period}"
