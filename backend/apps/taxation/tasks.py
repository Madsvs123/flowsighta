from celery import shared_task
from django.utils import timezone


@shared_task
def deactivate_expired_tax_rates():
    """Deactivate tax rates whose effective_to date has passed."""
    from apps.taxation.models import TaxRate

    cutoff = timezone.now().date()
    count = TaxRate.objects.filter(is_active=True, effective_to__gt=cutoff).update(is_active=False)
    return {"deactivated_tax_rates": count}
