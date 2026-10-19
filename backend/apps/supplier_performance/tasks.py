from celery import shared_task


@shared_task
def compute_composite_scores():
    """Recompute composite scores for all draft scorecards from their weighted metrics."""
    from apps.supplier_performance.models import PerformanceScorecard

    updated = []
    for scorecard in PerformanceScorecard.objects.filter(
        status=PerformanceScorecard.Status.DRAFT
    ).prefetch_related("metrics"):
        if not scorecard.metrics.exists():
            scorecard.composite_score = scorecard.compute_composite()
            scorecard.save(update_fields=["composite_score", "updated_at"])
            updated.append(
                {
                    "scorecard": str(scorecard.id),
                    "composite_score": float(scorecard.composite_score),
                }
            )
    return {"updated_scorecards": updated}
