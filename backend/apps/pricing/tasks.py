from datetime import timedelta

from celery import shared_task
from django.utils import timezone


@shared_task
def expire_discounts()
    """Mark discounts past their valid_to date as expired."""
    from apps.pricing.models import Discount

    cutoff = timezone.now().date()
    count = Discount.objects.filter(
        valid_to__lt=cutoff
    ).update(status=Discount.Status.EXPIRED)
    return {"expired_discounts": count}


@shared_task
def purge_stale_price_changes():
    """Delete price change records older than 2 years (retention housekeeping)."""
    from apps.pricing.models import PriceChange

    cutoff = timezone.now() - timedelta(days=730)
    count, _ = PriceChange.objects.filter(created_at__lt=cutoff).delete()
    return {"purged_price_changes": count}
