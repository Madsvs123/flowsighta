from django.db import models

from apps.core.models import AuditedModel, TenantModel


class ReplenishmentPolicy(TenantModel, AuditedModel):
    class Method(models.TextChoices):
        MIN_MAX = "min_max", "Min / Max"
        SS = "ss", "Safety Stock"
        DYNAMIC = "dynamic", "Dynamic"

    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="replenishment_policies"
    )
    warehouse = models.ForeignKey(
        "organizations.Warehouse", on_delete=models.CASCADE, related_name="replenishment_policies"
    )
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.MIN_MAX)
    min_stock = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    max_stock = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    lead_time_days = models.PositiveIntegerField(default=14)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("organization", "product", "warehouse")

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.name} ({self.method})"


class ReplenishmentRun(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"

    number = models.CharField(max_length=40)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    started_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("organization", "status")

    def __str__(self):
        return f"Replenishment run {self.number} ({self.status})"


class ReplenishmentLine(TenantModel):
    class Source(models.TextChoices):
        POLICY = "policy", "Policy"
        FORECAST = "forecast", "Forecast"
        MANUAL = "manual", "Manual"

    class Status(models.TextChoices):
        PROPOSED = "proposed", "Proposed"
        APPROVED = "approved", "Approved"
        SKIPPED = "skipped", "Skipped"

    run = models.ForeignKey(ReplenishmentRun, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="replenishment_lines"
    )
    warehouse = models.ForeignKey(
        "organizations.Warehouse", on_delete=models.CASCADE, related_name="replenishment_lines"
    )
    suggested_qty = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.POLICY)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "run", "status"])]

    def __str__(self):
        return f"{self.product.sku}: {self.suggested_qty} ({self.status})"


class ReplenishmentOrder(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        CANCELLED = "cancelled", "Cancelled"

    run = models.ForeignKey(ReplenishmentRun, on_delete=models.CASCADE, related_name="orders")
    supplier = models.ForeignKey(
        "suppliers.Supplier", on_delete=models.CASCADE, related_name="replenishment_orders"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "run", "status"])]

    def __str__(self):
        return f"Replenishment order for {self.supplier.name} ({self.status})"
