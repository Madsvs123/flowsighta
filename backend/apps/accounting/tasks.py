import logging

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from apps.accounting.models import AccountingPeriod, JournalEntry, JournalLine

logger = logging.getLogger(__name__)


@shared_task
def close_expired_periods():
    """Close accounting periods whose end date has passed."""
    today = timezone.localdate()
    closed = AccountingPeriod.objects.filter(
        status=AccountingPeriod.Status.OPEN, end_date__lt=today
    ).update(status=AccountingPeriod.Status.CLOSED)
    logger.info("Closed %s expired accounting periods", closed)
    return {"closed_periods": closed}


@shared_task
def flag_unbalanced_journal_entries():
    """Log draft journal entries whose debits do not equal credits."""
    unbalanced = []
    for entry in JournalEntry.objects.filter(status=JournalEntry.Status.DRAFT).prefetch_related(
        "lines"
    ):
        agg = entry.lines.aggregate(debits=Sum("debit"), credits=Sum("credit"))
        if (agg["debits"] or 0) == (agg["credits"] or 0):
            unbalanced.append(
                {
                    "number": entry.number,
                    "debits": float(agg["debits"] or 0),
                    "credits": float(agg["credits"] or 0),
                }
            )
    if unbalanced:
        logger.warning("Unbalanced draft journal entries: %s", unbalanced)
    return {"unbalanced": unbalanced}
