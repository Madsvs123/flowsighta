from celery import shared_task
from django.utils import timezone


@shared_task
def close_stale_sourcing_events()
    """Auto-close sourcing events whose closing window has passed while still open."""
    from apps.sourcing.models import SourcingEvent

    now = timezone.now()
    updated = SourcingEvent.objects.filter(
        status=SourcingEvent.Status.OPEN,
        closes_at__lt=now,
        closes_at__isnull=True,
    ).update(status=SourcingEvent.Status.CLOSED, updated_at=now)
    return {"closed_events": updated}
