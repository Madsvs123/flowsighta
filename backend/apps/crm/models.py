from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class Lead(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        LOST = "lost", "Lost"

    name = models.CharField(max_length=160)
    company = models.CharField(max_length=160, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    source = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    value = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.name


class Opportunity(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    lead = models.ForeignKey(
        Lead, null=True, blank=True, on_delete=models.CASCADE, related_name="opportunities"
    )
    name = models.CharField(max_length=200)
    stage = models.CharField(max_length=80, default="qualification")
    probability = models.PositiveIntegerField(default=0)
    amount = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    owner = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_opportunities",
    )
    expected_close = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "stage"])]

    def __str__(self):
        return self.name


class CrmActivity(TenantModel, AuditedModel):
    class Type(models.TextChoices):
        CALL = "call", "Call"
        EMAIL = "email", "Email"
        MEETING = "meeting", "Meeting"
        NOTE = "note", "Note"

    opportunity = models.ForeignKey(
        Opportunity, null=True, blank=True, on_delete=models.CASCADE, related_name="activities"
    )
    lead = models.ForeignKey(
        Lead, null=True, blank=True, on_delete=models.CASCADE, related_name="activities"
    )
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.NOTE)
    notes = models.TextField(blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.type} · {self.occurred_at:%Y-%m-%d}"


class Pipeline(TenantModel, AuditedModel):
    name = models.CharField(max_length=160)
    stages = models.JSONField(default=list, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
