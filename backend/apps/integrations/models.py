from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Integration(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        CONNECTED = "connected", "Connected"
        ERROR = "error", "Error"
        DISABLED = "disabled", "Disabled"

    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=120)
    config = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE, db_index=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "provider", "status"])]

    def __str__(self):
        return f"{self.name} · {self.provider}"


class IntegrationConnection(TenantModel):
    class Status(models.TextChoices):
        CONNECTED = "connected", "Connected"
        DISCONNECTED = "disconnected", "Disconnected"
        ERROR = "error", "Error"

    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name="connections")
    name = models.CharField(max_length=160)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DISCONNECTED, db_index=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "integration", "status"])]

    def __str__(self):
        return f"{self.integration.name} · {self.name}"


class IntegrationLog(TenantModel):
    class Direction(models.TextChoices):
        IN = "in", "In"
        OUT = "out", "Out"

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"

    connection = models.ForeignKey(IntegrationConnection, on_delete=models.CASCADE, related_name="logs")
    direction = models.CharField(max_length=10, choices=Direction.choices, default=Direction.IN)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUCCESS)
    payload_ref = models.CharField(max_length=200, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["organization", "connection", "status"])]

    def __str__(self):
        return f"{self.connection} · {self.direction} · {self.status}"


class WebhookEndpoint(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"

    name = models.CharField(max_length=200)
    url = models.URLField()
    events = models.JSONField(default=list, blank=True)
    secret = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.name
