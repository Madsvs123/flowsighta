from celery import shared_task


@shared_task
def recompute_list_ratings():
    """Recompute average supplier rating for every active approved list."""
    from django.db.models import Avg, Sum

    from apps.approved_lists.models import ApprovedList, ApprovedSupplier

    updated = []
    for list_obj in ApprovedList.objects.filter(status=ApprovedList.Status.ACTIVE):
        avg = list_obj.approved_suppliers.filter(
            status=ApprovedSupplier.Status.APPROVED, rating__gt=0
        ).aggregate(v=Sum("rating"))["v"]
        updated.append({"list": list_obj.name, "average_rating": float(avg or 0)})
    return {"lists": updated}
