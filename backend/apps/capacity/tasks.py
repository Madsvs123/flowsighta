from celery import shared_task


@shared_task
def compute_capacity_loads(organization_id=None):
    """Materialize daily capacity loads and refresh utilization for published plans."""
    from datetime import timedelta

    from django.utils import timezone

    from apps.capacity.models import CapacityLoad, CapacityPlan, CapacityProfile
    from apps.organizations.models import Organization

    today = timezone.now().date()
    loads_created = 0
    orgs = Organization.objects.filter(is_active=True, is_deleted=False)
    if organization_id:
        orgs = orgs.filter(id=organization_id)
    for org in orgs:
        for profile in CapacityProfile.objects.filter(organization=org, is_active=True):
            available = float(profile.available_hours or 0) * (float(profile.efficiency_pct or 100) / 100)
            plans = CapacityPlan.objects.filter(
                organization=org,
                profile=profile,
                period_end__gte=today,
                period_start__lte=today + timedelta(days=14),
            )
            for plan in plans:
                days = max((plan.period_end - plan.period_start).days + 1, 1)
                daily_planned = float(plan.planned_hours or 0) * days
                cursor = max(plan.period_start, today)
                end = min(plan.period_end, today + timedelta(days=14))
                while cursor <= end:
                    _, was_created = CapacityLoad.objects.update_or_create(
                        organization=org,
                        profile=profile,
                        date=cursor,
                        defaults={
                            "load_hours": daily_planned,
                            "available_hours": available,
                        },
                    )
                    if was_created:
                        loads_created += 1
                    cursor += timedelta(days=1)
                if plan.planned_hours:
                    plan.utilization_pct = min(
                        float(plan.actual_hours or 0) / float(plan.planned_hours) * 100, 100
                    )
                    plan.save(update_fields=["utilization_pct"])
    return {"loads_created": loads_created}
