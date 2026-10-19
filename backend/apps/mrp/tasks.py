from celery import shared_task


@shared_task
def run_mrp_for_organizations(organization_id=None):
    """Queue, execute and complete one MRP run per active organization."""
    from datetime import timedelta
    from decimal import Decimal

    from django.utils import timezone

    from apps.inventory.models import Product, StockItem
    from apps.mrp.models import MrpException, MrpRequirement, MrpRun
    from apps.organizations.models import Organization

    today = timezone.now().date()
    completed = 0
    orgs = Organization.objects.filter(is_active=True, is_deleted=False)
    if organization_id:
        orgs = orgs.filter(id=organization_id)
    for org in orgs:
        run = MrpRun.objects.create(
            organization=org,
            number=f"MRP-{org.slug}-{today:%Y%m%d}",
            status=MrpRun.Status.RUNNING,
            started_at=timezone.now(),
            horizon_days=90,
        )
        for product in Product.objects.filter(organization=org, is_active=True):
            stock = StockItem.objects.filter(organization=org, product=product).first()
            on_hand = Decimal(str(stock.on_hand if stock else 0))
            incoming = Decimal(str(stock.incoming if stock else 0))
            reorder = Decimal(str(stock.reorder_point if stock else 0))
            gross = max(reorder, Decimal("10"))
            scheduled = incoming
            projected = on_hand + scheduled - gross
            net = max(projected, Decimal("0"))
            lead = product.default_lead_time_days or 14
            MrpRequirement.objects.create(
                organization=org,
                run=run,
                product=product,
                gross_requirement=gross,
                scheduled_receipts=scheduled,
                projected_balance=projected,
                net_requirement=net,
                planned_order_qty=net,
                planned_order_date=today + timedelta(days=lead),
            )
            if net > 0:
                MrpException.objects.create(
                    organization=org,
                    run=run,
                    product=product,
                    type=MrpException.Type.SHORTAGE,
                    message=f"Net requirement {net} for {product.sku}",
                )
            elif projected < 0:
                MrpException.objects.create(
                    organization=org,
                    run=run,
                    product=product,
                    type=MrpException.Type.NEGATIVE_BALANCE,
                    message=f"Projected balance {projected} for {product.sku}",
                )
        run.status = MrpRun.Status.COMPLETED
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "finished_at"])
        completed += 1
    return {"runs_completed": completed}
