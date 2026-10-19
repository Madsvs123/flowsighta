from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from apps.vendor_invoices.models import VendorInvoice


@shared_task
def mark_overdue_invoices():
    """Report unpaid vendor invoices past their due date (amount + count)."""
    today = timezone.localdate()
    overdue = VendorInvoice.objects.filter(status__in=[VendorInvoice.Status.PAID, VendorInvoice.Status.VOID]).filter(
        due_date__lt=today
    )
    agg = overdue.aggregate(total=Sum("total")
    return {
        "overdue": overdue.count(),
        "overdue_amount": agg["total"] or 0,
        "numbers": list(overdue.values_list("number", flat=True)[:100]),
    }
