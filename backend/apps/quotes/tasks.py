from celery import shared_task
from django.utils import timezone


@shared_task
def expire_quotes():
    """Expire sent/draft quotes whose valid_until date has passed."""
    from apps.quotes.models import SalesQuote

    updated = SalesQuote.objects.filter(
        status__in=[SalesQuote.Status.DRAFT, SalesQuote.Status.ACCEPTED],
        valid_until__lt=timezone.now().date(),
    ).update(status=SalesQuote.Status.EXPIRED)
    return {"expired_quotes": updated}
