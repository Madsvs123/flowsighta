import logging

from celery import shared_task
from django.utils import timezone

from apps.tickets.models import SupportTicket

logger = logging.getLogger(__name__)

STALE_HOURS = 48


@shared_task
def escalate_stale_tickets(hours=STALE_HOURS):
    """Escalate tickets that have been open or in progress beyond the stale window."""
    cutoff = timezone.now() - timezone.timedelta(hours=hours)
    stale = SupportTicket.objects.filter(
        status__in=[SupportTicket.Status.OPEN, SupportTicket.Status.IN_PROGRESS],
        created_at__lt=cutoff,
    ).filter(priority=SupportTicket.Priority.URGENT)
    count = stale.update(
        priority=SupportTicket.Priority.URGENT,
        updated_at=timezone.now(),
    )
    logger.info("Escalated %s stale tickets", count)
    return {"escalated": count}


@shared_task
def aggregate_ticket_summary():
    """Aggregate ticket counts per status and priority for reporting."""
    summary = {"by_status": {}, "by_priority": {}}
    for status, _label in SupportTicket.Status.choices:
        summary["by_status"][status] = SupportTicket.objects.filter(status=status).count()
    for priority, _label in SupportTicket.Priority.choices:
        summary["by_priority"][priority] = SupportTicket.objects.filter(priority=priority).count()
    return summary
