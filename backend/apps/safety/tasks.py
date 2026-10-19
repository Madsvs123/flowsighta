import logging

from celery import shared_task
from django.utils import timezone

from apps.safety.models import Incident, SafetyTraining

logger = logging.getLogger(__name__)


@shared_task
def flag_expired_trainings():
    """Flag trainings whose expiry date has passed and reopen stale incidents."""
    today = timezone.localdate()
    expired = SafetyTraining.objects.filter(
        expiry_date__isnull=False, expiry_date__lt=today
    ).count()
    stale = Incident.objects.filter(
        status=Incident.Status.REPORTED, date__lt=today - timezone.timedelta(days=30)
    ).update(status=Incident.Status.INVESTIGATING)
    logger.info("Expired trainings: %s, stale incidents reopened: %s", expired, stale)
    return {"expired_trainings": expired, "stale_incidents_reopened": stale}


@shared_task
def aggregate_safety_summary():
    """Aggregate open incidents by type and severity per organization."""
    summary = {}
    for incident in Incident.objects.exclude(status=Incident.Status.CLOSED).select_related(
        "organization"
    ):
        org = summary.setdefault(
            str(incident.organization_id), {"total": 0, "by_type": {}, "by_severity": {}}
        )
        org["total"] += 1
        org["by_type"][incident.type] = org["by_type"].get(incident.type, 0) + 1
        org["by_severity"][incident.severity] = org["by_severity"].get(incident.severity, 0) + 1
    return summary
