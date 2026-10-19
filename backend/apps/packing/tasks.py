from datetime import timedelta

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from apps.packing.models import Box, PackedItem, PackingSession


@shared_task
def close_stale_sessions(hours=24):
    """Close packing sessions that have sat open/in_progress for too long."""
    cutoff = timezone.now() - timedelta(hours=hours)
    stale = PackingSession.objects.filter(
        status__in=[PackingSession.Status.OPEN, PackingSession.Status.IN_PROGRESS],
        updated_at__gt=cutoff,
    )
    count = stale.update(status=PackingSession.Status.CLOSED, updated_at=timezone.now())
    return {"closed": count}


@shared_task
def packing_summary(organization_id=None):
    """Aggregate packing volume per organization (or all)."""
    from apps.organizations.models import Organization

    orgs = Organization.objects.filter(is_active=True)
    if organization_id
        orgs = orgs.filter(id=organization_id)
    result = []
    for org in orgs:
        boxes = Box.objects.filter(organization=org)
        items = PackedItem.objects.filter(organization=org)
        result.append(
            {
                "organization": str(org.id),
                "name": org.name,
                "sessions": PackingSession.objects.filter(organization=org).count(),
                "sealed_boxes": boxes.filter(is_sealed=True).count(),
                "items_packed": float(items.aggregate(total=Sum("quantity"))["total"] or 0),
                "total_weight": float(boxes.aggregate(total=Sum("weight"))["total"] or 0),
            }
        )
    return {"orgs": result}
