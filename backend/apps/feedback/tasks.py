import logging

from celery import shared_task

from apps.feedback.models import Complaint, NpsScore

logger = logging.getLogger(__name__)


@shared_task
def compute_nps_scores():
    """Compute NPS per survey from submitted scores (0-10 → -100..100)."""
    result = {}
    for survey_id, scores in (
        NpsScore.objects.exclude(submitted_at__isnull=True)
        .values_list("survey_id", "score")
        .order_by("survey_id")
        .iterator(chunk_size=500)
    ):
        result.setdefault(survey_id, []).append(scores)
    nps_by_survey = {}
    for survey_id, scores in result.items():
        if not scores:
            continue
        promoters = sum(1 for s in scores if s >= 9)
        detractors = sum(1 for s in scores if s <= 6)
        nps_by_survey[survey_id] = round((promoters - detractors) / len(scores) * 100)
    logger.info("Computed NPS for %s surveys", len(nps_by_survey))
    return {"nps_by_survey": nps_by_survey}


@shared_task
def close_stale_complaints(days=30):
    """Close resolved complaints that have not been closed within N days."""
    from django.utils import timezone

    cutoff = timezone.now() - timezone.timedelta(days=days)
    count = Complaint.objects.filter(
        status=Complaint.Status.RESOLVED, updated_at__gt=cutoff
    ).update(status=Complaint.Status.CLOSED, updated_at=timezone.now())
    logger.info("Closed %s stale complaints", count)
    return {"closed": count}
