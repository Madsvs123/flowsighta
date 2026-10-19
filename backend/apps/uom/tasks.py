from celery import shared_task


@shared_task
def deactivate_unused_uoms():
    """Deactivate UOMs not referenced by any product and without conversions."""
    from apps.inventory.models import Product

    from apps.uom.models import Uom, UomConversion

    used_codes = set(Product.objects.filter(is_deleted=False).exclude(uom="").values_list("uom", flat=True))
    count = 0
    for uom in Uom.objects.filter(is_active=True):
        if uom.code in used_codes:
            continue
        if UomConversion.objects.filter(
            organization=uom.organization, from_uom=uom, is_active=True
        ).exists() and UomConversion.objects.filter(
            organization=uom.organization, to_uom=uom, is_active=True
        ).exists():
            continue
        uom.is_active = False
        uom.save(update_fields=["is_active", "updated_at"])
        count += 1
    return {"deactivated_uoms": count}
