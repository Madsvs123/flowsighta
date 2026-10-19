from celery import shared_task
from django.db.models import Sum

from apps.portfolios.models import CapitalRequest, Portfolio, PortfolioReview


@shared_task
def aggregate_portfolio_health()
    """Aggregate capital request and review stats per portfolio."""
    rows = []
    for portfolio in Portfolio.objects.all():
        requests = CapitalRequest.objects.filter(portfolio=portfolio)
        rows.append(
            {
                "portfolio": portfolio.name,
                "reviews": PortfolioReview.objects.filter(portfolio=portfolio).count(),
                "capital_requests": requests.count(),
                "pending_capital": requests.filter(
                    status__in=[CapitalRequest.Status.SUBMITTED, CapitalRequest.Status.APPROVED]
                ).count(),
                "approved_amount": float(
                    requests.filter(status=CapitalRequest.Status.APPROVED).aggregate(v=Sum("amount"))["v"] or 0
                ),
            }
        )
    return {"portfolios": rows}
