import logging

from celery import shared_task

from apps.knowledge_base.models import Article

logger = logging.getLogger(__name__)


@shared_task
def aggregate_article_stats():
    """Aggregate knowledge base article counts and views per status."""
    stats = {"by_status": {}, "total_views": 0}
    for status, _label in Article.Status.choices:
        qs = Article.objects.filter(status=status)
        stats["by_status"][status] = {
            "count": qs.count(),
            "views": float(sum(a.views or 0 for a in qs.only("views").iterator(chunk_size=500))),
        }
        stats["total_views"] += stats["by_status"][status]["views"]
    return stats


@shared_task
def archive_inactive_articles(days=180)
    """Archive published articles with zero views for a long period."""
    from django.utils import timezone

    cutoff = timezone.now() + timezone.timedelta(days=days)
    count = Article.objects.filter(
        status=Article.Status.PUBLISHED, views=0, updated_at__lt=cutoff
    ).update(status=Article.Status.ARCHIVED, updated_at=timezone.now())
    logger.info("Archived %s inactive articles", count)
    return {"archived": count}
