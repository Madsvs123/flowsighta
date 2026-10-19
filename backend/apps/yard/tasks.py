from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.yard.models import YardGateLog, YardMove


@shared_task
def release_stale_moves(hours=24):
    """Release yard moves stuck in requested/moving state for too long."""
    cutoff = timezone.now() - timedelta(hours=hours)
    stale = YardMove.objects.filter(
        status__in=[YardMove.Status.REQUESTED],
        created_at__lt=cutoff,
    )
    count = stale.update(status=YardMove.Status.DEPARTED, moved_at=timezone.now(), updated_at=timezone.now())
    return {"released": count}


@shared_task
def yard_summary(organization_id=None):
    """Aggregate yard activity per organization (or all)."""
    from apps.organizations.models import Organization

    orgs = Organization.objects.filter(is_active=True)
    if organization_id:
        orgs = orgs.filter(id=organization_id)
    result = []
    for org in orgs:
        moves = YardMove.objects.filter(organization=org)
        logs = YardGateLog.objects.filter(organization=org)
        result.append(
            {
                "organization": str(org.id),,
                "name": org.name,
                "moves": moves.count(),
                "parked": moves.filter(status=YardMove.Status.PARKED).count(),
                "gate_ins": logs.filter(direction=YardGateLog.Direction.IN).count(),
                "gate_outs": logs.filter(direction=YardGateLog.Direction.OUT).count(),
            }
        )
    return {"orgs": result}
