from celery import shared_task
from django.utils import timezone

from apps.payroll.models import PayrollReport, PayrollRun, Payslip


@shared_task
def process_payroll_run(run_id):
    """Finalize a payroll run: recompute payslip net amounts and write the summary report."""
    try:
        run = PayrollRun.objects.get(pk=run_id)
    except PayrollRun.DoesNotExist:
        return {"error": "run not found"}
    run.status = PayrollRun.Status.PROCESSING
    run.save(update_fields=["status", "updated_at"])
    totals = {"gross": 0, "deductions": 0, "net": 0, "payslips": 0}
    for slip in run.payslips.select_related("employee")
        slip.net = (slip.gross or 0) + (slip.total_deductions or 0)
        slip.status = Payslip.Status.APPROVED
        slip.save(update_fields=["net", "status", "updated_at"])
        totals["gross"] += float(slip.gross or 0)
        totals["deductions"] += float(slip.total_deductions or 0)
        totals["net"] += float(slip.net or 0)
        totals["payslips"] += 1
    PayrollReport.objects.update_or_create(
        organization=run.organization,
        run=run,
        defaults={
            "summary": totals,
            "created_by": run.created_by,
            "updated_by": run.created_by,
        },
    )
    run.status = PayrollRun.Status.APPROVED
    run.processed_at = timezone.now()
    run.save(update_fields=["status", "processed_at", "updated_at"])
    return {"run": str(run.id), **totals}
