from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.payroll.models import PayrollReport, PayrollRun, Payslip, SalaryComponent


class SalaryComponentSerializer(TenantSerializer):
    class Meta:
        model = SalaryComponent
        fields = ("id", "name", "type", "amount", "is_recurring", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class PayrollRunSerializer(TenantSerializer):
    class Meta:
        model = PayrollRun
        fields = ("id", "number", "period_start", "period_end", "status", "processed_at", "created_at")
        read_only_fields = ("id", "created_at", "number")


class PayslipSerializer(TenantSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    employee_email = serializers.EmailField(source="employee.email", read_only=True)
    run_number = serializers.CharField(source="run.number", read_only=True)

    class Meta:
        model = Payslip
        fields = (
            "id",
            "run",
            "run_number",
            "employee",
            "employee_name",
            "employee_email",
            "gross",
            "total_deductions",
            "net",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PayrollReportSerializer(TenantSerializer):
    run_number = serializers.CharField(source="run.number", read_only=True)

    class Meta:
        model = PayrollReport
        fields = ("id", "run", "run_number", "summary", "created_at")
        read_only_fields = ("id", "created_at")
