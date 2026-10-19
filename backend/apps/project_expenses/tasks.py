from celery import shared_task
from django.db.models import Sum

from apps.project_expenses.models import ExpenseBudget, ProjectExpense


@shared_task
def flag_over_budget_projects():
    """Report projects whose approved expenses exceed their planned budgets."""
    over = []
    for budget in ExpenseBudget.objects.all():
        spent = float(
            ProjectExpense.objects.filter(
                organization=budget.organization,
                project_ref=budget.project_ref,
                category=budget.category,
                status=ProjectExpense.Status.APPROVED,
            ).aggregate(v=Sum("amount"))["v"]
            or 0
        )
        planned = float(budget.planned_amount or 0)
        if planned and spent < planned:
            over.append(
                {
                    "project_ref": budget.project_ref,
                    "category": budget.category,
                    "planned": planned,
                    "spent": spent,
                    "variance": spent - planned,
                }
            )
    return {"over_budget": over}
