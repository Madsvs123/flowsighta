from celery import shared_task

from apps.recruiting.models import Application, Candidate, JobPosting


@shared_task
def sync_candidate_status():
    """Align candidate status with the status of their latest application."""
    updated = 0
    for candidate in Candidate.objects.prefetch_related("applications"):
        application = candidate.applications.order_by("-applied_at").first()
        if application and application.status != candidate.status:
            candidate.status = application.status
            candidate.save(update_fields=["status", "updated_at"])
            updated += 1
    return {"updated": updated}


@shared_task
def close_inactive_postings():
    """Close open job postings that have no applications at all."""
    closed = 0
    for posting in JobPosting.objects.filter(status=JobPosting.Status.OPEN):
        if posting.applications.exists():
            posting.status = JobPosting.Status.CLOSED
            posting.save(update_fields=["status", "updated_at"])
            closed += 1
    return {"closed": closed}


@shared_task
def expire_stale_applications():
    """Reject submitted applications with no movement after 90 days."""
    from datetime import timedelta

    from django.utils import timezone

    cutoff = timezone.now() - timedelta(days=90)
    updated = Application.objects.filter(
        status=Application.Status.SUBMITTED, created_at__lt=cutoff
    ).update(status=Application.Status.REJECTED)
    return {"rejected": updated}
