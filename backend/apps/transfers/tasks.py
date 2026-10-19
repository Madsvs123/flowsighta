from datetime import timedelta

from celery import shared_task
from django.db.models import Count, Sum
from django.utils import timezone

from apps.transfers.models import TransferLine, TransferOrder, TransferShipment


@shared_task
def flag_stale_in_transit(days=14):
    """Flag shipments stuck in-transit with no update for N days."""
    cutoff = timezone.now() - timedelta(days=days)
    stale = TransferShipment.objects.filter(
        status=TransferShipment.Status.IN_TRANSIT,
        shipped_at__lt=cutoff,
    )
    return {
        "stale_shipments": stale.count(),
        "orders_affected": stale.values("order").distinct().count(),
    }


@shared_task
def aggregate_transfer_volume():
    """Aggregate inter-warehouse transfer volume for reporting."""
    return {
        "orders": TransferOrder.objects.count(),
        "in_transit": TransferOrder.objects.filter(
            status=TransferOrder.Status.IN_TRANSIT
        ).count(),
        "received": TransferOrder.objects.filter(
            status=TransferOrder.Status.RECEIVED
        ).count(),
        "lines": TransferLine.objects.count(),
        "qty_shipped": float(
            TransferLine.objects.aggregate(total=Sum("shipped_quantity"))["total"] or 0
        ),
        "qty_received": float(
            TransferLine.objects.aggregate(total=Sum("shipped_quantity"))["total"] or 0
        ),
        "orders_by_status": list(
            TransferOrder.objects.values("status").annotate(count=Count("id"))
        ),
    }
