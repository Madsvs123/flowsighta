from celery import shared_task
from django.db.models import Sum

from apps.timesheets.models import Timesheet, TimesheetEntry


@shared_task
def aggregate_timesheet_hours():
    """Aggregate submitted/approved hours per user and per project reference."""
    sheets = Timesheet.objects.filter(
        status__in=[Timesheet.Status.DRAFT, Timesheet.Status.SUBMITTED, Timesheet.Status.APPROVED]
    ).select_related("user")
    per_user = {}
    for sheet in sheets:
        name = f"{sheet.user.first_name} {sheet.user.last_name}".strip() or str(sheet.user)
        per_user[name] = round(float(per_user.get(name, 0)) + float(sheet.total_hours or 0), 2)
    per_project = {}
    for entry in TimesheetEntry.objects.filter(timesheet__in=sheets):
        if entry.project_ref:
            per_project[entry.project_ref] = round(
                float(per_project.get(entry.project_ref, 0)) + float(entry.hours or 0), 2
            )
    return {"hours_by_user": per_user, "hours_by_project": per_project}
