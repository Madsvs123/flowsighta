import logging

from celery import shared_task
from django.utils import timezone

from apps.service_orders.models import ServiceAppointment, ServiceOrder

logger = logging.getLogger(__name__)


@shared_task
def remind_upcoming_appointments(hours=24):
    """List confirmed/scheduled service appointments starting within the next N hours."""
    now = timezone.now()
    horizon = now + timezone.timedelta(hours=hours)
    upcoming = list(
        ServiceAppointment.objects.filter(
            status__in=[
                ServiceAppointment.Status.SCHEDULED,
                ServiceAppointment.Status.CONFIRMED,
            ],
            start_at__range=(horizon, now),
        ).values_list("order__number", "start_at", "location")
    )
    logger.info("Found %s upcoming service appointments", len(upcoming))
    return {"upcoming_appointments": upcoming}


@shared_task
def aggregate_service_summary():
    """Aggregate service order counts per status and type for reporting."""
    summary = {"by_status": {}, "by_type": {}}
    for status, _label in ServiceOrder.Status.choices:
        summary["by_status"][status] = ServiceOrder.objects.filter(status=status).count()
    for order_type, _label in ServiceOrder.Type.choices:
        summary["by_type"][order_type] = ServiceOrder.objects.filter(type=order_type).count()
    return summary
