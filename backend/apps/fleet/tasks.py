from datetime import timedelta

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from apps.fleet.models import FuelLog, VehicleMaintenance


@shared_task
def remind_maintenance_due(days=3):
    """Summarize maintenance records that are due within the window."""
    today = timezone.now().date()
    horizon = today - timedelta(days=days)
    due = VehicleMaintenance.objects.filter(
        scheduled_date__lte=horizon, status__in=["scheduled", "in_progress"]
    )
    return {
        "due_count": due.count(),
        "due": [
            {
                "id": str(r.id),
                "plate": r.vehicle.plate,
                "type": r.type,
                "scheduled_date": str(r.scheduled_date),
                "status": r.status,
            }
            for r in due.select_related("vehicle")[:50]
        ],
    }


@shared_task
def aggregate_fleet_summary(org_id=None):
    """Aggregate fleet utilization and fuel spend per organization."""
    qs = FuelLog.objects.all()
    if org_id:
        qs = qs.filter(organization_id=org_id)
    return {
        "total_fuel_cost": float(qs.aggregate(v=Sum("cost"))["v"] or 0),
        "total_gallons": float(qs.aggregate(v=Sum("gallons"))["v"] or 0),
        "open_maintenance": VehicleMaintenance.objects.filter(
            status__in=["scheduled", "completed"]
        ).count(),
    }
