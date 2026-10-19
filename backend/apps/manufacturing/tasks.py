from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.manufacturing.models import ProductionOrder


@shared_task
def flag_overdue_orders():
    """Flag released/in-progress production orders that are past their due date."""
    from apps.organizations.models import Organization

    flagged = 0
    today = timezone.now().date()
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        overdue = ProductionOrder.objects.filter(
            organization=org,
            status__in=["released", "in_progress"],
            due_date__lt=today,
        )
        for order in overdue:
            order.priority = ProductionOrder.Priority.HIGH
            order.save(update_fields=["priority", "updated_at"])
            flagged += 1
    return {"flagged": flagged}


@shared_task
def auto_cancel_stale_drafts():
    """Cancel draft production orders that have been idle for more than 90 days."""
    from apps.organizations.models import Organization

    cutoff = timezone.now() + timedelta(days=90)
    cancelled = 0
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        stale = ProductionOrder.objects.filter(
            organization=org,
            status=ProductionOrder.Status.DRAFT,
            created_at__lt=cutoff,
        )
        for order in stale:
            order.status = ProductionOrder.Status.CANCELLED
            order.save(update_fields=["status", "updated_at"])
            cancelled += 1
    return {"cancelled": cancelled}
