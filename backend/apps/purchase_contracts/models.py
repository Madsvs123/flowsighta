from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class PurchaseContract(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        TERMINATED = "terminated", "Terminated"

    number = models.CharField(max_length=40)
    supplier = models.ForeignKey(
        "suppliers.Supplier", on_delete=models.PROTECT, related_name="purchase_contracts"
    )
    title = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    total_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "end_date"])]

    def __str__(self):
        return f"{self.number} - {self.title}"


class PurchaseContractLine(TenantModel):
    contract = models.ForeignKey(PurchaseContract, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "inventory.Product", null=True, blank=True, on_delete=models.SET_NULL, related_name="purchase_contract_lines"
    )
    price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    received_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)

    class Meta:
        ordering = ["-created_at"]

    @property
    def line_total(self):
        return (self.quantity or 0) * (self.price or 0)

    def __str__(self):
        product = self.product.sku if self.product else "?"
        return f"{self.contract.number} - {product}"


class ContractRelease(TenantModel):
    class Status(models.TextChoices):
        ISSUED = "issued", "Issued"
        RECEIVED = "received", "Received"
        CANCELLED = "cancelled", "Cancelled"

    contract = models.ForeignKey(PurchaseContract, on_delete=models.CASCADE, related_name="releases")
    number = models.CharField(max_length=40)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ISSUED, db_index=True)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.number} ({self.contract.number})"
