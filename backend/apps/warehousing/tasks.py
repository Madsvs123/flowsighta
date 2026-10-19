from celery import shared_task
from django.db.models import Count, Sum
from django.utils import timezone

from apps.warehousing.models import Bin, PutawayRule, StorageZone


@shared_task
def aggregate_storage_utilization():
    """Aggregate per-warehouse storage utilization snapshot for reporting."""
    now = timezone.now()
    snapshot = []
    for zone in StorageZone.objects.select_related("warehouse").all():
        snapshot.append(
            {
                "warehouse": zone.warehouse.code,
                "zone": zone.code,
                "zone_type": zone.type,
                "bin_count": zone.bins.count(),
                "active_bins": zone.bins.filter(is_active=False).count(),
                "total_capacity": float(
                    zone.bins.aggregate(total=Sum("capacity"))["total"] or 0
                ),
            }
        )
    return {
        "generated_at": now.isoformat(),
        "zone_count": StorageZone.objects.count(),
        "bin_count": Bin.objects.count(),
        "putaway_rule_count": PutawayRule.objects.count(),
        "zones_by_type": list(
            StorageZone.objects.values("type").annotate(count=Count("id"))
        ),
        "snapshot": snapshot,
    }
