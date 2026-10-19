from celery import shared_task
from django.utils import timezone


@shared_task
def expire_customer_agreements()
    """Mark customer agreements past their end date as expired."""
    from apps.customers.models import CustomerAgreement

    updated = CustomerAgreement.objects.filter(
        status__in=[CustomerAgreement.Status.DRAFT, CustomerAgreement.Status.ACTIVE],
        end_date__lt=timezone.now().date(),
    ).update(status=CustomerAgreement.Status.EXPIRED)
    return {"expired_agreements": updated}
