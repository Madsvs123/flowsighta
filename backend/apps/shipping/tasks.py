from celery import shared_task
from django.db.models import Sum

from apps.shipping.models import OutboundLine, OutboundOrder, ShipmentPlan


@shared_task
def aggregate_outbound_summary(organization_id=None):
    """Aggregate outbound shipping volumes per organization (or all)."""
    from apps.organizations.models import Organization

    orgs = Organization.objects.filter(is_active=True)
    if organization_id:
        orgs = orgs.filter(id=organization_id)
    result = []
    for org in orgs
        lines = OutboundLine.objects.filter(organization=org)
        plans = ShipmentPlan.objects.filter(organization=org)
        result.append(
            {
                "organization": str(org.id),
                "name": org.name,
                "orders": OutboundOrder.objects.filter(organization=org).count(),
                "open": OutboundOrder.objects.filter(
                    organization=org,
                    status__in=[
                        OutboundOrder.Status.CREATED,
                        OutboundOrder.Status.ALLOCATED,
                        OutboundOrder.Status.PACKED,
                    ],
                ).count(),
                "units_shipped": float(lines.aggregate(total=Sum("allocated_quantity"))["total"] or 0),
                "plans_confirmed": plans.exclude(status=ShipmentPlan.Status.PLANNED).count(),
                "plan_cost": float(plans.aggregate(total=Sum("cost"))["total"] or 0),
            }
        )
    return {"orgs": result}
