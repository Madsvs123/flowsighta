from django.db import models

from apps.core.models import AuditedModel, TenantModel


class SupplyChainEvent(TenantModel, AuditedModel):
    class Category(models.TextChoices):
        DELAYED_SHIPMENT = "delayed_shipment", "Delayed Shipment"
        SHORTAGE = "shortage", "Shortage"
        DAMAGED_GOODS = "damaged_goods", "Damaged Goods"
        MISSED_MILESTONE = "missed_milestone", "Missed Milestone"
        INVENTORY_RISK = "inventory_risk", "Inventory Risk"
        SUPPLIER_FAILURE = "supplier_failure", "Supplier Failure"
        DEMAND_CHANGE = "demand_change", "Demand Change"
        CUSTOMS = "customs", "Customs"
        QUALITY = "quality", "Quality"

    class Severity(models.TextChoices):
        INFO = "info", "Info"
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        DISMISSED = "dismissed", "Dismissed"

    number = models.CharField(max_length=40)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=40, choices=Category.choices, db_index=True)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    description = models.TextField(blank=True)
    source_type = models.CharField(max_length=40, blank=True)
    source_id = models.CharField(max_length=64, blank=True)
    supplier = models.ForeignKey(
        "suppliers.Supplier", null=True, blank=True, on_delete=models.SET_NULL, related_name="events"
    )
    shipment = models.ForeignKey(
        "logistics.Shipment", null=True, blank=True, on_delete=models.SET_NULL, related_name="events"
    )
    warehouse = models.ForeignKey(
        "organizations.Warehouse", null=True, blank=True, on_delete=models.SET_NULL, related_name="events"
    )
    product_sku = models.CharField(max_length=64, blank=True)
    detected_at = models.DateTimeField()
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    assignee = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_events"
    )
    impact_score = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-detected_at"]
        indexes = [models.Index(fields=["organization", "status", "severity"])]


class AlertRule(TenantModel, AuditedModel):
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=40)
    is_active = models.BooleanField(default=True)
    severity = models.CharField(max_length=20, default="low")
    condition = models.JSONField(default=dict)
    notify_roles = models.JSONField(default=list, blank=True)


class ResolutionAction(TenantModel, AuditedModel):
    event = models.ForeignKey(SupplyChainEvent, on_delete=models.CASCADE, related_name="actions")
    action_type = models.CharField(max_length=40)
    note = models.TextField()
    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="resolution_actions"
    )
