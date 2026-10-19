from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class Shift(TenantModel, AuditedModel):
    name = models.CharField(max_length=120)
    start_time = models.TimeField()
    end_time = models.TimeField()
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.name


class ShiftAssignment(TenantModel, AuditedModel):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shift_assignments",
    )
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name="assignments")
    date = models.DateField()

    class Meta:
        unique_together = ("organization", "shift", "date")
        ordering = ["date"]

    def __str__(self):
        return f"{self.employee} · {self.shift} · {self.date}"


class AttendanceRecord(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        LEAVE = "leave", "On Leave"

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta
        unique_together = ("organization", "employee", "date")
        ordering = ["-date"]
        indexes = [models.Index(fields=["organization", "date", "status"])]

    def __str__(self):
        return f"{self.employee} · {self.date} · {self.status}"


class OvertimeRequest(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="overtime_requests",
    )
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.employee} · {self.date} · {self.hours}h"
