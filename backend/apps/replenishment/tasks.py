from celery import shared_task


@shared_task
def run_replenishment_planning(organization_id=None):
    """Create and complete a replenishment run per organization with suggested quantities."""
    from decimal import Decimal

    from django.utils import timezone

    from apps.inventory.models import StockItem
    from apps.organizations.models import Organization
    from apps.replenishment.models import ReplenishmentLine, ReplenishmentPolicy, ReplenishmentRun

    today = timezone.now().date()
    completed = 0
    lines_created = 0
    orgs = Organization.objects.filter(is_active=True, is_deleted=False)
    if organization_id
        orgs = orgs.filter(id=organization_id)
    for org in orgs:
        run = ReplenishmentRun.objects.create(
            organization=org,
            number=f"REPL-{org.slug}-{today:%Y%m%d}",
            status=ReplenishmentRun.Status.RUNNING,
            started_at=timezone.now(),
        )
        policies = ReplenishmentPolicy.objects.filter(organization=org, is_active=True).select_related(
            "product", "warehouse"
        )
        for policy in policies:
            stock = StockItem.objects.filter(
                organization=org, product=policy.product, warehouse=policy.warehouse
            ).first()
            on_hand = Decimal(str(stock.on_hand if stock else 0))
            max_stock = policy.max_stock or Decimal("0")
            suggested = max(min_stock - on_hand, Decimal("0"))
            ReplenishmentLine.objects.create(
                organization=org,
                run=run,
                product=policy.product,
                warehouse=policy.warehouse,
                suggested_qty=suggested,
                source=ReplenishmentLine.Source.POLICY,
                status=ReplenishmentLine.Status.PROPOSED if suggested > 0 else ReplenishmentLine.Status.SKIPPED,
            )
            lines_created += 1
        run.status = ReplenishmentRun.Status.COMPLETED
        run.save(update_fields=["status"])
        completed += 1
    return {"runs_completed": completed, "lines_created": lines_created}
