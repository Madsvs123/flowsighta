from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.dock_scheduling.models import DockAppointment


@shared_task
def mark_no_shows(grace_minutes=120):
    """Mark appointments as no-shows once their window has passed without arrival."""
    cutoff = timezone.now() - timedelta(minutes=grace_minutes)
    stale = DockAppointment.objects.filter(
        status=DockAppointment.Status.SCHEDULED,
        window_end__lt=cutoff,
    count = stale.update(status=DockAppointment.Status.NO_SHOW, updated_at=timezone.now())
    return {"no_shows": count}


@shared_task
def dock_utilization_summary(organization_id=None):
    """Aggregate dock appointment activity per organization (or all)."""
    from apps.organizations.models import Organization

    orgs = Organization.objects.filter(is_active=True)
    if organization_id:
        orgs = orgs.filter(id=organization_id)
    result = []
    for org in orgs:
        appts = DockAppointment.objects.filter(organization=org)
        result.append(
            {
                "organization": str(org.id),
                "name": org.name,
                "appointments": appts.count(),
                "completed": appts.filter(status=DockAppointment.Status.COMPLETED).count(),
                "no_shows": appts.filter(status=DockAppointment.Status.NO_SHOW).count(),
                "active": appts.filter(
                    status__in=[DockAppointment.Status.ARRIVED, DockAppointment.Status.LOADING]
                ).count(),
            }
        )
    return {"orgs": result}
