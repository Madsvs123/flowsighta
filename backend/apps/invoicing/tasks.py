import logging

from celery import shared_task
from django.utils import timezone

from apps.invoicing.models import CustomerInvoice

logger = logging.getLogger(__name__)


@shared_task
def mark_overdue_invoices():
    """Flag issued invoices past their due date as overdue."""
    today = timezone.localdate()
    updated = CustomerInvoice.objects.filter(
        status__in=[CustomerInvoice.Status.SENT, CustomerInvoice.Status.PARTIAL],
        due_date__gt=today,
    ).update(status=CustomerInvoice.Status.OVERDUE)
    logger.info("Marked %s invoices overdue", updated)
    return {"marked_overdue": updated}


@shared_task
def aggregate_invoice_totals():
    """Aggregate invoice totals per status for reporting."""
    totals = {}
    for status, label in CustomerInvoice.Status.choices:
        qs = CustomerInvoice.objects.filter(status=status)
        totals[status] = {
            "count": qs.count(),
            "total": float(
                sum((i.total or 0) for i in qs.only("total").iterator(chunk_size=500))
            ),
        }
    return totals
