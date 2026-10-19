from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.maintenance.models import Equipment, MaintenanceOrder, MaintenancePlan


@shared_task
def generate_due_orders()
    """Generate maintenance orders for active plans whose next due date has arrived."""
    from apps.organizations.models import Organization

    created = 0
    today = timezone.now().date()
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        for plan in MaintenancePlan.objects.filter(organization=org, is_active=True):
            last = (
                MaintenanceOrder.objects.filter(
                    organization=org, plan=plan, completed_date__isnull=False
                )
                .order_by("-completed_date")
                .first()
            )
            due = last.completed_date + timedelta(days=plan.frequency_days) if last else None
            if due is None or due < today:
                exists = MaintenanceOrder.objects.filter(
                    organization=org,
                    plan=plan,
                    status__in=["scheduled", "in_progress"],
                ).exists()
                if not exists:
                    MaintenanceOrder.objects.create(
                        organization=org,
                        plan=plan,
                        equipment=plan.equipment,
                        status=MaintenanceOrder.Status.SCHEDULED,
                        scheduled_date=today,
                    )
                    created += 1
    return {"created": created}


@shared_task
def mark_overdue_orders():
    """Mark scheduled/in-progress maintenance orders past due as overdue."""
    from apps.organizations.models import Organization

    flagged = 0
    today = timezone.now().date()
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        overdue = MaintenanceOrder.objects.filter(
            organization=org,
            status__in=[MaintenanceOrder.Status.SCHEDULED, MaintenanceOrder.Status.IN_PROGRESS],
            scheduled_date__lt=today,
        )
        for order in overdue:
            order.status = MaintenanceOrder.Status.OVERDUE
            order.save(update_fields=["status", "updated_at"])
            if order.equipment.status == Equipment.Status.OPERATIONAL:
                order.equipment.status = Equipment.Status.MAINTENANCE
                order.equipment.save(update_fields=["status", "updated_at"])
            flagged += 1
    return {"flagged": flagged}
