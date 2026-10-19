from celery import shared_task


@shared_task
def expire_stale_schedules(organization_id=None):
    """Lock published schedules whose horizon has fully passed."""
    from django.utils import timezone

    from apps.scheduling.models import Schedule

    today = timezone.now().date()
    stale = Schedule.objects.filter(
        status=Schedule.Status.PUBLISHED, horizon_end__lt=today
    )
    if organization_id:
        stale = stale.filter(organization_id=organization_id)
    count = stale.count()
    for schedule in stale:
        schedule.status = Schedule.Status.LOCKED
        schedule.save(update_fields=["status", "updated_at"])
    return {"schedules_locked": count}


@shared_task
def release_blocked_tasks(organization_id=None):
    """Re-queue blocked tasks whose time window constraints are now satisfied."""
    from django.utils import timezone

    from apps.scheduling.models import ScheduleConstraint, ScheduleTask

    now = timezone.now()
    released = 0
    tasks = ScheduleTask.objects.filter(status=ScheduleTask.Status.BLOCKED).prefetch_related(
        "constraints"
    )
    if organization_id:
        tasks = tasks.filter(organization_id=organization_id)
    for task in tasks:
        time_windows = [
            c
            for c in task.constraints.all()
            if c.type == ScheduleConstraint.Type.TIME_WINDOW and isinstance(c.value, dict)
        ]
        # No time-window constraints => nothing keeps it blocked (manual blocks stay).
        if not time_windows:
            continue
        if all(
            (not v.get("start") or str(v["start"]) <= now.isoformat())
            and (not v.get("end") or str(v["end"]) <= now.isoformat())
            for v in time_windows
        ):
            task.status = ScheduleTask.Status.SCHEDULED
            task.save(update_fields=["status", "updated_at"])
            released += 1
    return {"tasks_released": released}
