from django.db import models

from apps.core.models import AuditedModel, TenantModel


class StorageZone(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        BULK = "bulk", "Bulk"
        PICK = "pick", "Pick"
        OVERSTOCK = "overstock", "Overstock"
        RETURN = "return", "Return"
        QUARANTINE = "quarantine", "Quarantine"

    warehouse = models.ForeignKey(
        "organizations.Warehouse", on_delete=models.CASCADE, related_name="zones"
    )
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=160)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.BULK)

    class Meta:
        unique_together = ("organization", "warehouse", "code")
        ordering = ["warehouse__code", "code"]
        indexes = [models.Index(fields=["organization", "warehouse", "type"])]

    def __str__(self):
        return f"{self.warehouse.code}/{self.code}"


class Bin(TenantModel):
    zone = models.ForeignKey(StorageZone, on_delete=models.CASCADE, related_name="bins")
    code = models.CharField(max_length=40)
    capacity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "zone", "code")
        ordering = ["zone__code", "code"]
        indexes = [models.Index(fields=["organization", "is_active"])]

    def __str__(self):
        return f"{self.zone.code}/{self.code}"


class PutawayRule(TenantModel):
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=80, blank=True)
    zone = models.ForeignKey(
        StorageZone, null=True, blank=True, on_delete=models.SET_NULL, related_name="putaway_rules"
    )
    priority = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["priority", "name"]
        indexes = [models.Index(fields=["organization", "category"])]

    def __str__(self):
        return self.name
