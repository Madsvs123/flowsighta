from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.attendance.models import AttendanceRecord, OvertimeRequest, ShiftAssignment


@shared_task
def auto_mark_absent():
    """Create absent records for employees assigned a shift today with no attendance record."""
    today = timezone.now().date()
    assigned = ShiftAssignment.objects.filter(date=today).values_list("employee_id", flat=True)
    recorded = AttendanceRecord.objects.filter(date=today).values_list("employee_id", flat=True)
    missing = set(assigned) - set(recorded)
    created = 0
    for assignment in ShiftAssignment.objects.filter(date=today, employee_id__in=missing).select_related("organization"):
        _, was_created = AttendanceRecord.objects.get_or_create(
            organization=assignment.organization,
            employee_id=assignment.employee_id,
            date=today,
            defaults={"status": AttendanceRecord.Status.ABSENT},
        )
        if was_created:
            created += 1
    return {"marked_absent": created}


@shared_task
def expire_stale_overtime():
    """Auto-reject overtime requests still pending after 30 days past their date."""
    cutoff = timezone.now().date() - timedelta(days=30)
    updated = OvertimeRequest.objects.filter(
        status=OvertimeRequest.Status.PENDING, date__gt=cutoff
    ).update(status=OvertimeRequest.Status.REJECTED)
    return {"rejected": updated}
