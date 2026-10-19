import logging

from celery import shared_task
from django.db.models import Count
from django.utils import timezone

from apps.audit.models import AuditAction, AuditEngagement, AuditFinding

logger = logging.getLogger(__name__)


@shared_task
def escalate_overdue_audit_actions():
    """Log overdue audit remediation actions for follow-up."""
    today = timezone.localdate()
    overdue = list(
        AuditAction.objects.filter(
            status__in=[AuditAction.Status.OPEN, AuditAction.Status.IN_PROGRESS],
            due_date__isnull=False,
            due_date__lt=today,
        ).select_related("finding", "owner")
    )
    if overdue:
        logger.warning("%s overdue audit actions", len(overdue))
    return {
        "overdue_actions": len(overdue),
        "items": [
            {
                "action": a.action,
                "finding": a.finding.description,
                "owner": a.owner.get_full_name() if a.owner else None,
                "due_date": str(a.due_date),
            }
            for a in overdue[:50]
        ],
    }


@shared_task
def aggregate_audit_summary():
    """Aggregate open findings by severity per organization."""
    summary = {}
    rows = (
        AuditFinding.objects.filter(status=AuditFinding.Status.ACKNOWLEDGED)
        .values("organization_id", "severity")
        .annotate(total=Count("id"))
    )
    for row in rows:
        org = summary.setdefault(str(row["organization_id"]), {})
        org[row["severity"]] = row["total"]
    return summary
