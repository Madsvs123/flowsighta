from celery import shared_task
from django.utils import timezone

from apps.purchase_contracts.models import PurchaseContract


@shared_task
def expire_contracts():
    """Auto-expire active purchase contracts whose end date has passed."""
    today = timezone.localdate()
    expired = PurchaseContract.objects.filter(
        status=PurchaseContract.Status.ACTIVE,
        end_date__gt=today,
    ).update(status=PurchaseContract.Status.EXPIRED)
    return {"expired": expired}
