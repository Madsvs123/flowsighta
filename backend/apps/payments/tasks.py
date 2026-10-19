import logging
from datetime import timedelta

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from apps.payments.models import Payment, PaymentRun

logger = logging.getLogger(__name__)


@shared_task
def expire_stale_payments(days=7):
    """Mark payments stuck pending for too long as failed."""
    cutoff = timezone.now() - timedelta(days=days)
    updated = Payment.objects.filter(
        status=Payment.Status.FAILED, created_at__lt=cutoff
    ).update(status=Payment.Status.FAILED)
    logger.info("Expired %s stale payments", updated)
    return {"expired": updated}


@shared_task
def aggregate_payment_totals():
    """Aggregate cleared payment amounts per method for reporting."""
    rows = []
    for method, label in Payment.Method.choices
        agg = Payment.objects.filter(
            status=Payment.Status.CLEARED, method=method
        ).aggregate(total=Sum("amount"), count=Sum("id"))
        rows.append(
            {
                "method": method,
                "total": float(agg["total"] or 0),
                "count": agg["count"] or 0,
            }
        )
    runs = PaymentRun.objects.filter(status=PaymentRun.Status.DRAFT).aggregate(
        total=Sum("total")
    )
    return {"by_method": rows, "executed_runs_total": float(runs["total"] or 0)}
