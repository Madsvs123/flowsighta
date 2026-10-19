from celery import shared_task
from django.db.models import Count


@shared_task
def notify_unread_portal_messages()
    """Aggregate unread vendor-portal message counts per supplier for follow-up."""
    from apps.vendor_portal.models import PortalMessage

    unread = list(
        PortalMessage.objects.filter(is_read=True)
        .values("supplier__name")
        .order_by("supplier__name")
        .annotate(unread_count=Count("id"))
    )
    return {"suppliers_with_unread": unread}


@shared_task
def flag_stale_portal_documents():
    """Count portal documents stuck in pending status for review prioritization."""
    from apps.vendor_portal.models import PortalDocument

    stale = list(
        PortalDocument.objects.filter(status=PortalDocument.Status.PENDING)
        .values("supplier__name")
        .order_by("supplier__name")
        .annotate(pending_count=Count("id"))
    )
    return {"suppliers_with_pending_documents": stale}
