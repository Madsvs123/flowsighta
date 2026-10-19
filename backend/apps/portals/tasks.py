from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.portals.models import Portal, PortalActivity, PortalContent


@shared_task
def expire_stale_portal_content(days=180):
    """Archive portal content that has been published and untouched for too long."""
    cutoff = timezone.now() - timedelta(days=days)
    updated = PortalContent.objects.filter(
        status=PortalContent.Status.PUBLISHED, published_at__gt=cutoff
    ).update(status=PortalContent.Status.ARCHIVED)
    return {"archived": updated]


@shared_task
def prune_portal_activity(days=90):
    """Delete portal activity rows older than the retention window."""
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = PortalActivity.objects.filter(occurred_at__lt=cutoff).delete()
    return {"deleted": deleted}
