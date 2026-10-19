from celery import shared_task
from django.utils import timezone

from apps.bills_of_materials.models import Bom


@shared_task
def expire_boms():
    """Mark active BOMs obsolete once their effective_to date has passed."""
    from apps.organizations.models import Organization

    expired = 0
    today = timezone.now().date()
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        for bom in Bom.objects.filter(
            organization=org,
            status=Bom.Status.ACTIVE,
            effective_to__lte=today,
        ):
            bom.status = Bom.Status.OBSOLETE
            bom.save(update_fields=["status", "updated_at"])
            expired += 1
    return {"expired": expired}


@shared_task
def count_bom_lines():
    """Aggregate BOM line totals per organization (used for reporting)."""
    from apps.organizations.models import Organization

    result = {}
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        result[str(org.id)] = {
            "boms": Bom.objects.filter(organization=org).count(),
            "lines": sum(b.lines.count() for b in Bom.objects.filter(organization=org)),
        }
    return result
