from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class Department(TenantModel, AuditedModel):
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=160)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_departments",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "code")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_LEAVE = "on_leave", "On Leave"
        TERMINATED = "terminated", "Terminated"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )
    employee_no = models.CharField(max_length=40)
    job_title = models.CharField(max_length=160, blank=True)
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employees",
    )
    manager = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reports",
    )
    hire_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        unique_together = ("organization", "employee_no")
        ordering = ["employee_no"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return f"{self.employee_no} {self.user.get_full_name() or self.user.email}"


class EmploymentHistory(TenantModel, AuditedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="employment_history")
    position = models.CharField(max_length=160)
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employment_history",
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["start_date"]
        indexes = [models.Index(fields=["organization", "employee"])]

    def __str__(self):
        return f"{self.employee} · {self.position}"
