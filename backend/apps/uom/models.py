from django.db import models

from apps.core.models import TenantModel


class Uom(TenantModel):
    class Dimension(models.TextChoices):
        COUNT = "count", "Count"
        WEIGHT = "weight", "Weight"
        VOLUME = "volume", "Volume"
        LENGTH = "length", "Length"

    code = models.CharField(max_length=24)
    name = models.CharField(max_length=120)
    dimension = models.CharField(max_length=20, choices=Dimension.choices, default=Dimension.COUNT)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        unique_together = ("organization", "name")
        indexes = [models.Index(fields=["organization", "dimension", "is_active"])]

    def __str__(self):
        return self.code


class UomConversion(TenantModel):
    from_uom = models.ForeignKey(Uom, on_delete=models.CASCADE, related_name="conversions_from")
    to_uom = models.ForeignKey(Uom, on_delete=models.CASCADE, related_name="conversions_to")
    factor = models.DecimalField(max_digits=14, decimal_places=6)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["from_uom__code", "to_uom__code"]
        unique_together = ("organization", "from_uom", "to_uom")
        indexes = [models.Index(fields=["organization", "from_uom", "to_uom", "is_active"])]

    def __str__(self):
        return f"{self.from_uom.code} -> {self.to_uom.code} x{self.factor}"
