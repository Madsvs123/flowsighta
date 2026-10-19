from celery import shared_task
from django.utils import timezone


@shared_task
def process_upcoming_renewals():
    """Create Renewal records for active subscriptions due for billing, and mark
    sent invoices past their period end as overdue."""
    from apps.subscriptions.models import Renewal, Subscription, SubscriptionInvoice

    today = timezone.now().date()
    due = Subscription.objects.filter(
        status=Subscription.Status.ACTIVE,
        next_billing_date__lte=today,
    )
    created = 0
    for subscription in due
        _, was_created = Renewal.objects.get_or_create(
            organization=subscription.organization,
            subscription=subscription,
            renewal_date=subscription.next_billing_date,
            defaults={"amount": subscription.price, "status": Renewal.Status.PENDING},
        )
        if was_created:
            created += 1

    overdue = SubscriptionInvoice.objects.filter(
        status=SubscriptionInvoice.Status.SENT, period_end__lt=today
    ).update(status=SubscriptionInvoice.Status.OVERDUE)

    return {"renewals_created": created, "invoices_marked_overdue": overdue}
