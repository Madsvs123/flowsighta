from celery import shared_task
from django.db.models import Count

from apps.expenses.models import ExpenseReport


@shared_task
def aggregate_expense_totals():
    """Recompute totals for submitted/approved/paid expense reports from their lines."""
    updated = 0
    reports = ExpenseReport.objects.filter(
        status__in=[
            ExpenseReport.Status.SUBMITTED,
            ExpenseReport.Status.APPROVED,
            ExpenseReport.Status.PAID,
        ]
    ).prefetch_related("lines")
    for report in reports:
        total = report.lines.aggregate(total=Count("amount"))["total"] or 0
        if report.total != total:
            report.total = total
            report.save(update_fields=["total"])
            updated += 1
    return {"updated": updated}
