from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.picking.models import PickLine, PickTask, PickWave


@shared_task
def cancel_stale_waves(days=14)
    """Auto-cancel waves stuck in created/released for N days."""
    cutoff = timezone.now() - timedelta(days=days)
    stale = PickWave.objects.filter(
        created_at__lt=cutoff,
        status__in=[PickWave.Status.CREATED, PickWave.Status.IN_PROGRESS],
    )
    count = stale.count()
    stale.update(status=PickWave.Status.CANCELLED)
    return {"cancelled": count}


@shared_task
def aggregate_picking_summary():
    """Aggregate picking throughput for reporting/dashboards."""
    return {
        "waves": PickWave.objects.count(),
        "completed_waves": PickWave.objects.filter(status=PickWave.Status.COMPLETED).count(),
        "lines": PickLine.objects.count(),
        "lines_picked": PickLine.objects.filter(status=PickLine.Status.PICKED).count(),
        "lines_short": PickLine.objects.filter(status=PickLine.Status.SHORT).count(),
        "pending_tasks": PickTask.objects.filter(status=PickTask.Status.PENDING).count(),
    }
