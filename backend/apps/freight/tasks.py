from celery import shared_task
from django.db.models import Avg, Count
from django.utils import timezone

from apps.freight.models import FreightQuote


@shared_task
def expire_stale_quotes()
    """Mark quotes past their validity window as expired."""
    today = timezone.now().date()
    stale = FreightQuote.objects.filter(
        valid_until__gt=today, status__in=[FreightQuote.Status.DRAFT, FreightQuote.Status.ACTIVE]
    )
    count = stale.update(status=FreightQuote.Status.EXPIRED, updated_at=timezone.now())
    return {"expired_quotes": count}


@shared_task
def aggregate_freight_summary(org_id=None):
    """Aggregate per-organization freight quote statistics."""
    qs = FreightQuote.objects.all()
    if org_id:
        qs = qs.filter(organization_id=org_id)
    summary = {
        "total_quotes": qs.count(),
        "by_mode": dict(qs.values_list("mode").annotate(count=Count("id"))),
        "by_status": dict(qs.values_list("status").annotate(count=Count("id"))),
        "avg_rate": float(qs.aggregate(avg=Avg("transit_days"))["avg"] or 0),
    }
    return summary
