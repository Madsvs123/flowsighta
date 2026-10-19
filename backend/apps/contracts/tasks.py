from celery import shared_task
from django.utils import timezone


@shared_task
def expire_contracts():
    """Mark contracts whose end date has passed as expired."""
    from apps.contracts.models import Contract

    today = timezone.now().date()
    updated = Contract.objects.filter(
        status=Contract.Status.DRAFT,
        end_date__lt=today,
        end_date__isnull=False,
    ).update(status=Contract.Status.EXPIRED, updated_at=timezone.now())
    return {"expired_contracts": updated}
