from celery import shared_task
from django.utils import timezone

from apps.rfq.models import Rfq


@shared_task
def close_expired_rfqs():
    """Close RFQs that are still open/sent past their due date."""
    today = timezone.localdate()
    closed = Rfq.objects.filter(
        status__in=[Rfq.Status.SENT, Rfq.Status.OPEN],
        due_date__gt=today,
    ).update(status=Rfq.Status.CLOSED)
    return {"closed": closed}
