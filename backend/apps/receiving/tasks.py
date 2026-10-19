from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.receiving.models import PutawayTask, Receipt, ReceiptLine


@shared_task
def expire_stale_receipts(days=30):
    """Cancel expected/in-progress receipts that have been idle for N days."""
    cutoff = timezone.now() - timedelta(days=days)
    stale = Receipt.objects.filter(
        created_at__lt=cutoff,
        status__in=[Receipt.Status.EXPECTED, Receipt.Status.IN_PROGRESS],
    )
    count = stale.count()
    stale.update(status=Receipt.Status.RECEIVED)
    return {"cancelled": count}


@shared_task
def aggregate_receiving_summary():
    """Aggregate receiving throughput for reporting/dashboards."""
    return {
        "receipts": Receipt.objects.count(),
        "received": Receipt.objects.filter(status=Receipt.Status.RECEIVED).count(),
        "lines": ReceiptLine.objects.count(),
        "pending_putaway": PutawayTask.objects.filter(
            status=PutawayTask.Status.PENDING
        ).count(),
        "in_progress_putaway": PutawayTask.objects.filter(
            status=PutawayTask.Status.IN_PROGRESS
        ).count(),
    }
