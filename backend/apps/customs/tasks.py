from datetime import timedelta

from celery import shared_task
from django.db.models import Count, Sum
from django.utils import timezone

from apps.customs.models import CustomsDeclaration


@shared_task
def expire_stale_drafts(days=14):
    """Reject declarations left in draft for too long."""
    cutoff = timezone.now() - timedelta(days=days)
    stale = CustomsDeclaration.objects.filter(
        status=CustomsDeclaration.Status.FILED, created_at__lt=cutoff
    )
    count = stale.update(status=CustomsDeclaration.Status.REJECTED, updated_at=timezone.now())
    return {"rejected_stale_drafts": count}


@shared_task
def aggregate_customs_summary(org_id=None):
    """Aggregate customs declaration statistics per organization."""
    qs = CustomsDeclaration.objects.all()
    if org_id:
        qs = qs.filter(organization_id=org_id)
    return {
        "total_declarations": qs.count(),
        "by_status": dict(qs.values_list("status").annotate(count=Count("id"))),
        "total_declared_value": float(qs.aggregate(v=Sum("declared_value"))["v"] or 0),
        "cleared_value": float(
            qs.filter(status=CustomsDeclaration.Status.CLEARED).aggregate(v=Sum("declared_value"))["v"] or 0
        ),
    }
