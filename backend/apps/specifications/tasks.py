from celery import shared_task


@shared_task
def deactivate_empty_templates():
    """Deactivate specification templates that have no items defined."""
    from django.db.models import Count

    from apps.specifications.models import SpecificationTemplate

    count = 0
    for template in SpecificationTemplate.objects.filter(is_active=True).annotate(
        item_total=Count("values")
    ):
        if template.item_total == 0:
            template.is_active = False
            template.save(update_fields=["is_active", "updated_at"])
            count += 1
    return {"deactivated_templates": count}
