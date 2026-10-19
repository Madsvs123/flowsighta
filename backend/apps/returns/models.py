from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class ReturnOrder(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        SUPPLIER = "supplier", "Supplier"

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        APPROVED = "approved", "Approved"
        RECEIVED = "received", "Received"
        INSPECTED = "inspected", "Inspected"
        RESTOCKED = "restocked", "Restocked"
        CLOSED = "closed", "Closed"
        REJECTED = "rejected", "Rejected"

    number = models.CharField(max_length=40)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.CUSTOMER)
    reference = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED, db_index=True)
    reason = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="return_orders",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.number


class ReturnLine(TenantModel):
    class Condition(models.TextChoices):
        NEW = "new", "New"
        USED = "used", "Used"
        DAMAGED = "damaged", "Damaged"
        DEFECTIVE = "defective", "Defective"

    class Disposition(models.TextChoices):
        RESTOCK = "restock", "Restock"
        SCRAP = "scrap", "Scrap"
        REFURBISH = "refurbish", "Refurbish"
        RETURN_TO_VENDOR = "return_to_vendor", "Return to Vendor"

    order = models.ForeignKey(ReturnOrder, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("inventory.Product", on_delete=models.PROTECT, related_name="return_lines")
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.NEW)
    disposition = models.CharField(max_length=24, choices=Disposition.choices, default=Disposition.RESTOCK)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "order"])]

    def __str__(self):
        return f"{self.order.number} · {self.product_id}"


class RestockTask(TenantModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"

    line = models.ForeignKey(ReturnLine, on_delete=models.CASCADE, related_name="restock_tasks")
    warehouse = models.ForeignKey(
        "organizations.Warehouse",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="restock_tasks",
    )
    bin = models.CharField(max_length=60, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.line.order.number} / {self.bin or 'unassigned'}"
