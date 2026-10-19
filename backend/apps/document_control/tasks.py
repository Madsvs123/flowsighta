import logging

from celery import shared_task
from django.db.models import Count
from django.utils import timezone

from apps.document_control.models import Document, DocumentApproval, DocumentRevision

logger = logging.getLogger(__name__)


@shared_task
def flag_obsolete_documents():
    """Obsolete approved documents that have not been revised recently."""
    cutoff = timezone.now() - timezone.timedelta(days=365)
    obsoleted = (
        Document.objects.filter(
            status=Document.Status.APPROVED,
            revisions__approved_at__gt=cutoff,
        )
        .distinct()
        .update(status=Document.Status.OBSOLETE)
    )
    logger.info("Obsoleted %s stale documents", obsoleted)
    return {"obsoleted_documents": obsoleted}


@shared_task
def remind_pending_approvals():
    """List documents stuck in review with no approval decision."""
    pending = []
    for revision in DocumentRevision.objects.filter(
        document__status=Document.Status.IN_REVIEW
    ).select_related("document"):
        if not revision.approvals.exists():
            pending.append(
                {
                    "code": revision.document.code,
                    "title": revision.document.title,
                    "version": revision.version,
                }
            )
    return {"documents_pending_approval": pending}


@shared_task
def aggregate_document_summary():
    """Aggregate document counts by type and status per organization."""
    summary = {}
    rows = (
        Document.objects.values("organization_id", "type", "status")
        .annotate(total=Count("id"))
        .order_by("organization_id", "type", "status")
    )
    for row in rows:
        org = summary.setdefault(str(row["organization_id"]), {"by_type": {}, "by_status": {}})
        org["by_type"][row["type"]] = org["by_type"].get(row["type"], 0) + row["total"]
        org["by_status"][row["status"]] = org["by_status"].get(row["status"], 0) + row["total"]
    return summary
