from celery import shared_task
from django.utils import timezone

from apps.leave.models import LeaveBalance, LeaveRequest


@shared_task
def cancel_stale_leave_requests()
    """Cancel pending leave requests whose start date has already passed."""
    today = timezone.now().date()
    updated = LeaveRequest.objects.filter(
        status=LeaveRequest.Status.PENDING, start_date__gt=today
    ).update(status=LeaveRequest.Status.CANCELLED)
    return {"cancelled": updated}


@shared_task
def rollover_leave_balances():
    """Create next-year balances for employees who hold a current-year balance."""
    today = timezone.now().date()
    next_year = today.year + 1
    created = 0
    for balance in LeaveBalance.objects.select_related("policy", "organization").filter(year=today.year):
        if not balance.policy.is_active:
            continue
        _, was_created = LeaveBalance.objects.get_or_create(
            organization=balance.organization,
            employee=balance.employee,
            policy=balance.policy,
            year=next_year,
            defaults={
                "allocated": balance.policy.days_per_year,
                "used": 0,
                "remaining": balance.policy.days_per_year,
            },
        )
        if was_created:
            created += 1
    return {"created": created}
