from celery import shared_task


@shared_task
def deactivate_stale_variants()
    """Deactivate catalog variants whose parent product is inactive."""
    from apps.inventory.models import Product

    count = 0
    for product in Product.objects.filter(is_deleted=False, is_active=False):
        updated = product.variants.filter(is_active=True).update(is_active=False)
        count += updated
    return {"deactivated_variants": count}
