from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.core.services import notify_user
from apps.employees.models import Employee


@shared_task
def flag_work_anniversaries(days_ahead=7):
    """Notify employees whose hire-date anniversary falls within the next week."""
    today = timezone.now().date()
    notified = 0
    for employee in Employee.objects.select_related("user", "organization").filter(status=Employee.Status.ACTIVE):
        if not employee.hire_date:
            continue
        try:
            anniversary = employee.hire_date.replace(year=today.year)
        except ValueError:
            anniversary = today  # Feb 29 edge case — fall back to today
        if today <= anniversary <= today + timedelta(days=days_ahead - 1):
            if employee.user:
                notify_user(
                    employee.organization,
                    employee.user,
                    "Work anniversary",
                    f"{employee.user.get_full_name() or employee.user.email} — hired {employee.hire_date:%d %b %Y}.",
                    category="hr",
                )
                notified += 1
    return {"notified": notified}


@shared_task
def flag_terminated_employees():
    """Mark employees with no employment history as terminated after a long tenure gap."""
    cutoff = timezone.now().date() - timedelta(days=365)
    flagged = Employee.objects.filter(
        status=Employee.Status.ACTIVE,
        hire_date__lt=cutoff,
        employment_history__isnull=True,
    ).update(status=Employee.Status.TERMINATED)
    return {"flagged": flagged}
