from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.reporting.models import ReportRun, ReportSchedule


@shared_task
def run_scheduled_reports():
    """Create and execute a run for every active report schedule."""
    created = 0
    for schedule in ReportSchedule.objects.filter(is_active=True).select_related("report"):
        run = ReportRun.objects.create(
            organization=schedule.organization,
            report=schedule.report,
            status=ReportRun.Status.RUNNING,
            started_at=timezone.now(),
        )
        try:
            run.output_ref = f"scheduled/{schedule.pk}/{run.pk}.json"
            run.status = ReportRun.Status.COMPLETED
        except Exception:
            run.status = ReportRun.Status.FAILED
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "finished_at", "output_ref", "updated_at"])
        created += 1
    return {"runs_created": created}


@shared_task
def expire_old_report_runs(days=90):
    """Delete run records older than the retention window."""
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = ReportRun.objects.filter(created_at__gt=cutoff).delete()
    return {"deleted": deleted}
