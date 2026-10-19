from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.employees.models import Department, Employee, EmploymentHistory


class DepartmentSerializer(TenantSerializer):
    manager_name = serializers.CharField(source="manager.get_full_name", read_only=True)

    class Meta:
        model = Department
        fields = ("id", "code", "name", "manager", "manager_name", "is_active", "created_at")
        read_only_fields = ("id", "created_at"


class EmployeeSerializer(TenantSerializer):
    name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    manager_name = serializers.CharField(source="manager.get_full_name", read_only=True)

    class Meta:
        model = Employee
        fields = (
            "id",
            "user",
            "name",
            "email",
            "employee_no",
            "job_title",
            "department",
            "department_name",
            "manager",
            "manager_name",
            "hire_date",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class EmploymentHistorySerializer(TenantSerializer):
    employee_name = serializers.CharField(source="employee.user.get_full_name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = EmploymentHistory
        fields = (
            "id",
            "employee",
            "employee_name",
            "position",
            "department",
            "department_name",
            "start_date",
            "end_date",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
