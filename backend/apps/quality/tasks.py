from celery import shared_task
from django.utils import timezone

from apps.quality.models import CorrectiveAction, NonConformance


@shared_task
def escalate_overdue_corrective_actions():
    """Escalate corrective actions past due date to high priority status."""
    from apps.organizations.models import Organization

    escalated = 0
    today = timezone.now().date()
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        overdue = CorrectiveAction.objects.filter(
            organization=org,
            status__in=[CorrectiveAction.Status.OPEN, CorrectiveAction.Status.IN_PROGRESS],
            due_date__lt=today,
        )
        for ca in overdue
            ca.status = CorrectiveAction.Status.IN_PROGRESS
            ca.save(update_fields=["status", "updated_at"])
            escalated += 1
    return {"escalated": escalated}


@shared_task
def auto_close_resolved_non_conformances():
    """Close non-conformances whose corrective actions are all verified."""
    from apps.organizations.models import Organization

    closed = 0
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        open_ncs = NonConformance.objects.filter(
            organization=org,
            status__in=[NonConformance.Status.OPEN, NonConformance.Status.INVESTIGATING],
        )
        for nc in open_ncs:
            actions = list(nc.corrective_actions.all())
            if actions and any(a.status == CorrectiveAction.Status.VERIFIED for a in actions):
                nc.status = NonConformance.Status.CLOSED
                nc.save(update_fields=["status", "updated_at"])
                closed += 1
    return {"closed": closed}
