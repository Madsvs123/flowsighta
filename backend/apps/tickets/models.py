from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class TicketCategory(TenantModel):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    name = models.CharField(max_length=120)
    default_priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "name")

    def __str__(self):
        return self.name


class SupportTicket(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        WAITING = "waiting", "Waiting"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    number = models.CharField(max_length=32)
    subject = models.CharField(max_length=200)
    category = models.ForeignKey(
        TicketCategory, on_delete=models.PROTECT, related_name="tickets"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requested_tickets",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("organization", "number")
        indexes = [models.Index(fields=["organization", "status", "priority"])]

    def __str__(self):
        return f"{self.number} · {self.subject}"


class TicketMessage(TenantModel):
    ticket = models.ForeignKey(
        SupportTicket, on_delete=models.CASCADE, related_name="messages"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ticket_messages",
    )
    body = models.TextField()
    is_internal = models.BooleanField(default=False)

     class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["organization", "ticket", "created_at"])]

    def __str__(self):
        return f"Message on {self.ticket.number}"


class TicketSla(TenantModel):
    name = models.CharField(max_length=120)
    response_minutes = models.PositiveIntegerField(default=24)
    resolution_minutes = models.PositiveIntegerField(default=2880)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "name")

    def __str__(self):
        return self.name
