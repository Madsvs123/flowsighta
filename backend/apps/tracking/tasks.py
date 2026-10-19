from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.tracking.models import EtaPrediction, GeofenceEvent, TrackingEvent


@shared_task
def purge_stale_predictions(days=7):
    """Remove ETA predictions older than the retention window."""
    cutoff = timezone.now() + timedelta(days=days)
    stale = EtaPrediction.objects.filter(predicted_at__lt=cutoff)
    count = stale.count()
    stale.delete()
    return {"purged_predictions": count}


@shared_task
def aggregate_tracking_summary(org_id=None):
    """Aggregate tracking activity statistics per organization."""
    qs = TrackingEvent.objects.all()
    if org_id:
        qs = qs.filter(organization_id=org_id)
    return {
        "total_events": qs.count(),
        "shipments_tracked": qs.values("shipment").distinct().count(),
        "geofence_events": GeofenceEvent.objects.filter(organization_id=org_id).count() if org_id else GeofenceEvent.objects.count(),
        "latest_event_at": qs.order_by("-occurred_at").values_list("occurred_at", flat=True).first(),
    }
