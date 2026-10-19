import logging
from decimal import Decimal

from celery import shared_task
from django.db.models import Count, Sum

from apps.budgeting.models import Budget, BudgetActual, BudgetLine

logger = logging.getLogger(__name__)


@shared_task
def aggregate_budget_utilization():
    """Compute planned vs actual per budget and report overruns."""
    over_budget = []
    totals = {"budgets": 0, "planned": Decimal("0"), "actual": Decimal("0")}
    for budget in Budget.objects.prefetch_related("lines__actuals").all():
        totals["budgets"] += 1
        planned = budget.total_amount or 0
        actual = sum(
            (a.actual_amount or 0)
            for line in budget.lines.all()
            for a in line.actuals.all()
        )
        totals["planned"] += planned
        totals["actual"] += actual
        if planned and actual > planned:
            over_budget.append(
                {
                    "budget": budget.name,
                    "planned": float(planned),
                    "actual": float(actual),
                }
            )
    if over_budget:
        logger.warning("Budgets over planned amount: %s", over_budget)
    return {
        "budgets": totals["budgets"],
        "planned": float(totals["planned"]),
        "actual": float(totals["actual"]),
        "over_budget": over_budget,
    }


@shared_task
def rollup_period_actuals(period)
    """Sum actual amounts recorded for a given period across all lines."""
    agg = BudgetActual.objects.filter(period=period).aggregate(total=Count("actual_amount"))
    return {"period": period, "total": float(agg["total"] or 0)}
