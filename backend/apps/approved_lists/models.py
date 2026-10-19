from django.db import models

from apps.core.models import AuditedModel, TenantModel


class ApprovedList(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "name")
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.name


class ApprovedSupplier(TenantModel):
    class Status(models.TextChoices):
        APPROVED = "approved", "Approved"
        PENDING = "pending", "Pending"
        ON_HOLD = "on_hold", "On Hold"
        REVOKED = "revoked", "Revoked"

    list = models.ForeignKey(ApprovedList, on_delete=models.CASCADE, related_name="approved_suppliers")
    supplier = models.ForeignKey(
        "suppliers.Supplier", on_delete=models.CASCADE, related_name="approved_list_entries"
    )
    rating = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    notes = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["approved_at", "created_at"]
        unique_together = ("organization", "list", "supplier")
        indexes = [models.Index(fields=["organization", "list", "status"])]

    def __str__(self):
        return f"{self.list.name} · {self.supplier.name}"
