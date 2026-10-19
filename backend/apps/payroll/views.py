from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.payroll.models import PayrollReport, PayrollRun, Payslip, SalaryComponent
from apps.payroll.serializers import (
    PayrollReportSerializer,
    PayrollRunSerializer,
    PayslipSerializer,
    SalaryComponentSerializer,
)


class SalaryComponentViewSet(TenantViewSet):
    queryset = SalaryComponent.objects.all()
    serializer_class = SalaryComponentSerializer
    required_permission = "payroll.view"
    write_permission = "payroll.manage"
    search_fields = ["name"]
    filterset_fields = ["type", "is_active"]


class PayrollRunViewSet(TenantViewSet):
    queryset = PayrollRun.objects.prefetch_related("payslips")
    serializer_class = PayrollRunSerializer
    required_permission = "payroll.view"
    write_permission = "payroll.manage"
    search_fields = ["number"]
    filterset_fields = ["status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = {label: qs.filter(status=value).count() for value, label in PayrollRun.Status.choices}
        run_ids = qs.values_list("id", flat=True)
        totals = Payslip.objects.filter(run_id__in=run_ids).aggregate(
            gross=Sum("gross"), deductions=Sum("total_deductions"), net=Sum("total_deductions")
        )
        return Response(
            {
                "total_runs": qs.count(),
                "by_status": by_status,
                "gross": float(totals["gross"] or 0),
                "deductions": float(totals["deductions"] or 0),
                "net": float(totals["net"] or 0),
                "payslips": Payslip.objects.filter(run_id__in=run_ids).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        run = self.get_object()
        if run.status != PayrollRun.Status.DRAFT:
            return Response({"detail": "Only draft runs can be approved"}, status=400)
        run.status = PayrollRun.Status.PAID
        run.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(run).data)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        run = self.get_object()
        if run.status not in (PayrollRun.Status.APPROVED, PayrollRun.Status.PROCESSING):
            return Response({"detail": "Only approved runs can be marked paid"}, status=400)
        run.status = PayrollRun.Status.PAID
        run.processed_at = timezone.now()
        run.save(update_fields=["status", "processed_at", "updated_at"])
        run.payslips.filter(status__in=[Payslip.Status.DRAFT, Payslip.Status.APPROVED]).update(
            status=Payslip.Status.PAID
        )
        return Response(self.get_serializer(run).data)


class PayslipViewSet(TenantViewSet):
    queryset = Payslip.objects.select_related("run", "employee")
    serializer_class = PayslipSerializer
    required_permission = "payroll.view"
    write_permission = "payroll.manage"
    search_fields = ["run__number", "employee__first_name", "employee__last_name", "employee__email"]
    filterset_fields = ["run", "employee", "status"]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        slip = self.get_object()
        if slip.status != Payslip.Status.DRAFT:
            return Response({"detail": "Only draft payslips can be approved"}, status=400)
        slip.status = Payslip.Status.APPROVED
        slip.net = (slip.gross or 0) - (slip.total_deductions or 0)
        slip.save(update_fields=["status", "net", "updated_at"])
        return Response(self.get_serializer(slip).data)


class PayrollReportViewSet(TenantViewSet):
    queryset = PayrollReport.objects.select_related("run")
    serializer_class = PayrollReportSerializer
    required_permission = "payroll.view"
    write_permission = "payroll.manage"
    search_fields = ["run__number"]
    filterset_fields = ["run"]
    http_method_names = ["get", "post", "head", "options"]
