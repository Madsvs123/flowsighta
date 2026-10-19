from celery import shared_task
from django.db.models import Count, Sum

from apps.cycle_counts.models import CountLine, CycleCount


@shared_task
def flag_count_discrepancies():
    """Recompute variance on completed counts and flag unresolved lines."""
    flagged = 0
    for line in CountLine.objects.filter(
        count__status=CycleCount.Status.COMPLETED,
        status__in=[CountLine.Status.PENDING, CountLine.Status.MATCHED],
    ).select_related("count"):
        variance = (line.counted_qty or 0) - (line.system_qty or 0
        new_status = (
            CountLine.Status.MATCHED
            if variance == 0
            else CountLine.Status.VARIANCE
        )
        if new_status != line.status:
            line.status = new_status
            line.variance = variance
            line.save(update_fields=["status", "variance", "updated_at"])
            if new_status == CountLine.Status.VARIANCE:
                flagged += 1
    return {"new_variance_flags": flagged}


@shared_task
def aggregate_cycle_count_accuracy():
    """Aggregate count accuracy for reporting/dashboards."""
    lines = CountLine.objects.all()
    total = lines.count()
    matched = lines.filter(status=CountLine.Status.MATCHED).count()
    return {
        "counts": CycleCount.objects.count(),
        "completed": CycleCount.objects.filter(status=CycleCount.Status.COMPLETED).count(),
        "approved": CycleCount.objects.filter(status=CycleCount.Status.APPROVED).count(),
        "lines": total,
        "matched_lines": matched,
        "accuracy_pct": round(matched / total * 100, 2) if total else 0,
        "total_variance": float(lines.aggregate(total=Sum("variance"))["total"] or 0),
        "lines_by_status": list(lines.values("status").annotate(count=Count("id"))),
    }
