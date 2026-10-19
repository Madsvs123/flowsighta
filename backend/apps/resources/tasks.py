from celery import shared_task
from django.utils import timezone

from apps.resources.models import Resource, ResourceAllocation


@shared_task
def close_stale_allocations():
    """Mark confirmed allocations whose end date has passed as done and free the resource."""
    stale = ResourceAllocation.objects.filter(
        status=ResourceAllocation.Status.PLANNED, end_date__lt=timezone.now().date()
    )
    count = stale.count()
    for allocation in stale:
        allocation.status = ResourceAllocation.Status.DONE
        allocation.save(update_fields=["status", "updated_at"])
    for resource in Resource.objects.filter(status=Resource.Status.ALLOCATED):
        if not resource.allocations.exclude(status=ResourceAllocation.Status.DONE).exists():
            resource.status = Resource.Status.AVAILABLE
            resource.save(update_fields=["status", "updated_at"])
    return {"allocations_closed": count}
