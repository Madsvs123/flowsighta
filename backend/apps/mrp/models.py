from django.db import models

from apps.core.models import AuditedModel, TenantModel


class MrpRun(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    number = models.CharField(max_length=40)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    horizon_days = models.PositiveIntegerField(default=90)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("organization", "number")

    def __str__(self):
        return f"MRP run {self.number} ({self.status})"


class MrpRequirement(TenantModel):
    run = models.ForeignKey(MrpRun, on_delete=models.CASCADE, related_name="requirements")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="mrp_requirements"
    )
    gross_requirement = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    scheduled_receipts = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    projected_balance = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    net_requirement = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    planned_order_qty = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    planned_order_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["planned_order_date"]
        indexes = [models.Index(fields=["organization", "run", "product"])]

    def __str__(self):
        return f"{self.product.sku}: net {self.net_requirement}"


class MrpException(TenantModel):
    class Type(models.TextChoices):
        SHORTAGE = "shortage", "Shortage"
        EXCESS = "excess", "Excess"
        LEAD_TIME = "lead_time", "Lead Time"
        NEGATIVE_BALANCE = "negative_balance", "Negative Balance"

    run = models.ForeignKey(MrpRun, on_delete=models.CASCADE, related_name="exceptions")
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.CASCADE, related_name="mrp_exceptions"
    )
    type = models.CharField(max_length=32, choices=Type.choices)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "run", "type"])]

    def __str__(self):
        return f"{self.type} on {self.product.sku}"
