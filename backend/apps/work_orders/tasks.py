from celery import shared_task
from django.utils import timezone

from apps.work_orders.models import WorkOrder


@shared_task
def remind_overdue_work_orders():
    """Escalate open work orders past their due date to urgent priority."""
    from apps.organizations.models import Organization

    escalated = 0
    today = timezone.now().date()
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        overdue = WorkOrder.objects.filter(
            organization=org,
            status__in=["open", "assigned", "in_progress", "on_hold"],
            due_date__lt=today,
            priority__in=["low", "medium"],
        )
        for order in overdue:
            order.priority = WorkOrder.Priority.URGENT
            order.save(update_fields=["priority", "updated_at"])
            escalated += 1
    return {"escalated": escalated}


@shared_task
def auto_close_stale_orders():
    """Cancel open work orders that have seen no activity in 120 days."""
    from datetime import timedelta

    from apps.organizations.models import Organization

    cutoff = timezone.now() - timedelta(days=120)
    cancelled = 0
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        stale = WorkOrder.objects.filter(
            organization=org,
            status=WorkOrder.Status.OPEN,
            created_at__gt=cutoff,
        )
        for order in stale:
            order.status = WorkOrder.Status.CANCELLED
            order.save(update_fields=["status", "updated_at"])
            cancelled += 1
    return {"cancelled": cancelled}
