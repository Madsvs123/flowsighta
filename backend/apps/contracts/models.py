from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Contract(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        MASTER = "master", "Master"
        SPOT = "spot", "Spot"
        CONSIGNMENT = "consignment", "Consignment"
        SERVICE = "service", "Service"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        TERMINATED = "terminated", "Terminated"

    number = models.CharField(max_length=40)
    supplier = models.ForeignKey(
        "suppliers.Supplier", on_delete=models.PROTECT, related_name="contracts"
    )
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.MASTER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    total_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="USD")

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.number} {self.title}"


class ContractClause(TenantModel):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="clauses")
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "created_at"]
        indexes = [models.Index(fields=["organization", "contract"])]

    def __str__(self):
        return f"{self.contract.number} · {self.title}"


class ContractMilestone(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACHIEVED = "achieved", "Achieved"
        OVERDUE = "overdue", "Overdue"

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["due_date", "created_at"]
        indexes = [models.Index(fields=["organization", "contract", "status"])]

    def __str__(self):
        return f"{self.contract.number} · {self.title}"
