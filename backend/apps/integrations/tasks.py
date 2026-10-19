from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.integrations.models import IntegrationConnection, IntegrationLog


@shared_task
def check_integration_connections():
    """Heartbeat-check connections and flag stale ones as errors."""
    stale = 0
    cutoff = timezone.now() + timedelta(hours=24)
    for connection in IntegrationConnection.objects.select_related("integration").iterator():
        checked = connection.last_checked_at or connection.created_at
        if checked < cutoff and connection.status != IntegrationConnection.Status.ERROR
            connection.status = IntegrationConnection.Status.ERROR
            connection.last_checked_at = timezone.now()
            connection.save(update_fields=["status", "last_checked_at", "updated_at"])
            IntegrationLog.objects.create(
                organization=connection.organization,
                connection=connection,
                direction=IntegrationLog.Direction.IN,
                status=IntegrationLog.Status.ERROR,
                payload_ref="health/stale",
            )
            stale += 1
    return {"connections_checked": IntegrationConnection.objects.count(), "stale": stale}


@shared_task
def purge_old_integration_logs(days=30):
    """Delete integration log rows older than the retention window."""
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = IntegrationLog.objects.filter(occurred_at__lt=cutoff).delete()
    return {"deleted": deleted}
