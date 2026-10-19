from django.utils import timezone

from celery import shared_task

from apps.accounts.models import Invitation


@shared_task
def expire_stale_invitations()
    now = timezone.now()
    updated = Invitation.objects.filter(status=Invitation.Status.PENDING, expires_at__gt=now).update(
        status=Invitation.Status.EXPIRED
    )
    return {"expired": updated}
