from celery import shared_task
from django.db.models import Q, Sum


@shared_task
def rollup_pipeline()
    """Aggregate CRM pipeline totals (leads, opportunities, stage values)."""
    from apps.crm.models import Lead, Opportunity

    leads = Lead.objects.filter(is_deleted=False)
    opps = Opportunity.objects.filter(is_deleted=False)
    return {
        "leads": leads.count(),
        "qualified_leads": leads.filter(status=Lead.Status.QUALIFIED).count(),
        "opportunities": opps.count(),
        "open_value": float(
            opps.filter(status=Opportunity.Status.OPEN).aggregate(total=Sum("amount"))["total"] or 0
        ),
        "won_value": float(
            opps.filter(status=Opportunity.Status.WON).aggregate(
                total=Sum("amount", filter=Q(status=Opportunity.Status.WON))
            )["total"]
            or 0
        ),
    }
