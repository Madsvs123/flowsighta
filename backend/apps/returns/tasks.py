from celery import shared_task
from django.db.models import Sum

from apps.returns.models import RestockTask, ReturnLine, ReturnOrder


@shared_task
def returns_summary(organization_id=None):
    """Aggregate return flow volumes per organization (or all)."""
    from apps.organizations.models import Organization

    orgs = Organization.objects.filter(is_active=True)
    if organization_id:
        orgs = orgs.filter(id=organization_id)
    result = []
    for org in orgs:
        lines = ReturnLine.objects.filter(organization=org)
        result.append(
            {
                "organization": str(org.id),
                "name": org.name,
                "returns": ReturnOrder.objects.filter(organization=org).count(),
                "open": ReturnOrder.objects.filter(
                    organization=org,
                    status__in=[
                        ReturnOrder.Status.REQUESTED,
                        ReturnOrder.Status.APPROVED,
                        ReturnOrder.Status.RECEIVED,
                        ReturnOrder.Status.INSPECTED,
                    ],
                ).count(),
                "units_returned": float(lines.aggregate(total=Sum("quantity"))["total"] or 0),
                "pending_restock": RestockTask.objects.filter(
                    organization=org, status=RestockTask.Status.COMPLETED
                ).count(),
            }
        )
    return {"orgs": result}
