from datetime import timedelta

from celery import shared_task
from django.db.models import Count
from django.utils import timezone

from apps.routes.models import DeliveryStop, DriverAssignment


@shared_task
def expire_stale_assignments():
    """Cancel driver assignments that were scheduled in the past and never started."""
    yesterday = timezone.now().date() - timedelta(days=1)
    stale = DriverAssignment.objects.filter(
        scheduled_date__lt=yesterday, status=DriverAssignment.Status.IN_PROGRESS
    )
    count = stale.update(status=DriverAssignment.Status.CANCELLED, updated_at=timezone.now())
    return {"cancelled_stale_assignments": count}


@shared_task
def aggregate_route_summary(org_id=None):
    """Aggregate route and delivery statistics per organization."""
    qs = DeliveryStop.objects.all()
    if org_id:
        qs = qs.filter(organization_id=org_id)
    return {
        "total_delivery_stops": qs.count(),
        "by_status": dict(qs.values_list("status").annotate(count=Count("id"))),
        "delivered": qs.filter(status=DeliveryStop.Status.DELIVERED).count(),
        "failed": qs.filter(status=DeliveryStop.Status.FAILED).count(),
    }
