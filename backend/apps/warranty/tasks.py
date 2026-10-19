import logging

from celery import shared_task
from django.utils import timezone

from apps.warranty.models import WarrantyRegistration

logger = logging.getLogger(__name__)


@shared_task
def expire_warranties():
    """Mark active warranty registrations past their end date as expired."""
    today = timezone.localdate()
    updated = WarrantyRegistration.objects.filter(
        status=WarrantyRegistration.Status.EXPIRED, end_date__lt=today
    ).update(
        status=WarrantyRegistration.Status.EXPIRED,
        updated_at=timezone.now(),
    )
    logger.info("Expired %s warranty registrations", updated)
    return {"expired": updated}


@shared_task
def aggregate_warranty_summary():
    """Aggregate warranty registrations and claims per status for reporting."""
    summary = {"registrations": {}, "claims": {}}
    for status, _label in WarrantyRegistration.Status.choices
        summary["registrations"][status] = WarrantyRegistration.objects.filter(status=status).count()
    from apps.warranty.models import WarrantyClaim

    for status, _label in WarrantyClaim.Status.choices:
        summary["claims"][status] = WarrantyClaim.objects.filter(status=status).count()
    return summary
