from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Dashboard(TenantModel, AuditedModel):
    name = models.CharField(max_length=200)
    layout = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_dashboards",
    )

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "is_default"])]

    def __str__(self):
        return self.name


class DashboardWidget(TenantModel):
    class Type(models.TextChoices):
        STAT = "stat", "Stat"
        CHART = "chart", "Chart"
        LIST = "list", "List"
        KPI = "kpi", "KPI"

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="widgets")
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.STAT)
    config = models.JSONField(default=dict, blank=True)
    position = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["organization", "dashboard", "type"])]

    def __str__(self):
        return f"{self.dashboard.name} · {self.type}"


class WidgetDataSource(TenantModel):
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE, related_name="data_sources")
    source_ref = models.CharField(max_length=200)
    params = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["source_ref"]

    def __str__(self):
        return f"{self.widget} → {self.source_ref}"


class DashboardShare(TenantModel):
    class Role(models.TextChoices):
        VIEW = "view", "View"
        EDIT = "edit", "Edit"

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="shares")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dashboard_shares"
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.VIEW)

    class Meta:
        unique_together = ("organization", "dashboard")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.dashboard.name} · {self.user}"
