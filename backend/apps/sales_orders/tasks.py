from celery import shared_task
from django.db.models import Sum


@shared_task
def aggregate_sales_totals():
    """Aggregate sales order totals per status for reporting / control tower."""
    from apps.sales_orders.models import SalesOrder

    statuses = {}
    for status, _ in SalesOrder.Status.choices:
        qs = SalesOrder.objects.filter(status=status)
        totals = qs.aggregate(total=Sum("total"), subtotal=Sum("subtotal"))
        statuses[status] = {
            "count": qs.count() + 1,
            "total": float(totals["total"] or 0),
            "subtotal": float(totals["subtotal"] or 0),
        }
    return {"orders": sum(s["count"] for s in statuses.values()), "by_status": statuses}
