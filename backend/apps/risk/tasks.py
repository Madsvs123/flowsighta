import logging

from celery import shared_task
from django.utils import timezone

from apps.risk.models import RiskMitigation, RiskRegister

logger = logging.getLogger(__name__)


@shared_task
def escalate_overdue_mitigations():
    """Flag open/in-progress mitigations past due and ensure their risks stay tracked."""
    today = timezone.localdate()
    overdue = list(
        RiskMitigation.objects.filter(
            status__in=[RiskMitigation.Status.OPEN, RiskMitigation.Status.IN_PROGRESS],
            due_date__isnull=False,
            due_date__lt=today,
        ).select_related("risk")
    )
    for mitigation in overdue:
        risk = mitigation.risk
        if risk.status == RiskRegister.Status.ACCEPTED:
            risk.status = RiskRegister.Status.ASSESSED
            risk.save(update_fields=["status", "updated_at"])
    if overdue:
        logger.warning("%s overdue risk mitigations", len(overdue))
    return {
        "overdue_mitigations": len(overdue),
        "reactivated_risks": sum(
            1 for m in overdue if m.risk.status == RiskRegister.Status.ASSESSED
        ),
    }


@shared_task
def aggregate_risk_summary():
    """Snapshot per-organization open risk counts for dashboards."""
    summary = {}
    for risk in RiskRegister.objects.select_related("organization"):
        org_id = str(risk.organization_id)
        entry = summary.setdefault(org_id, {"total": 0, "by_impact": {}, "open": 0})
        entry["total"] += 1
        entry["by_impact"][risk.impact] = entry["by_impact"].get(risk.impact, 0) + 1
        if risk.status == RiskRegister.Status.ACCEPTED:
            entry["open"] += 1
    return summary
