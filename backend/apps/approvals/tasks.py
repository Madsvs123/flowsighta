from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.approvals.models import ApprovalRequest


@shared_task
def escalate_stale_approvals(days=3):
    """Report approval requests that have been pending beyond the threshold
    so operators can chase or cancel them."""
    cutoff = timezone.now() - timedelta(hours=days)
    stale = ApprovalRequest.objects.filter(
        status=ApprovalRequest.Status.PENDING,
        requested_at__lt=cutoff,
    )
    return {
        "stale_requests": stale.count(),
        "references": list(stale.values_list("reference", flat=True)[:50]),
    }
