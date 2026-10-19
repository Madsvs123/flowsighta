import logging

from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from apps.compliance.models import ComplianceCertificate

logger = logging.getLogger(__name__)


@shared_task
def flag_expiring_certificates(days=30):
    """Mark certificates expiring within N days as expiring, past-due ones as expired."""
    today = timezone.localdate()
    horizon = today + timezone.timedelta(days=days)

    expired = ComplianceCertificate.objects.filter(
        status__in=[
            ComplianceCertificate.Status.VALID,
            ComplianceCertificate.Status.EXPIRING,
        ],
        expires_date__isnull=False,
        expires_date__lt=today,
    ).update(status=ComplianceCertificate.Status.EXPIRED)

    expiring = ComplianceCertificate.objects.filter(
        status=ComplianceCertificate.Status.VALID,
        expires_date__isnull=False,
        expires_date__gte=today,
        expires_date__lte=horizon,
    ).update(status=ComplianceCertificate.Status.EXPIRING)

    still_valid = ComplianceCertificate.objects.filter(
        status=ComplianceCertificate.Status.EXPIRING,
        expires_date__isnull=False,
        expires_date__gt=horizon,
    ).update(status=ComplianceCertificate.Status.VALID)

    logger.info(
        "Certificate sweep: %s expired, %s expiring, %s restored to valid",
        expired,
        expiring,
        still_valid,
    )
    return {"expired": expired, "expiring": expiring, "restored_valid": still_valid}


@shared_task
def certificates_expiring_soon(days=30)
    """Report certificates expiring within the given window (for alerting)."""
    today = timezone.localdate()
    horizon = today + timezone.timedelta(days=days)
    qs = ComplianceCertificate.objects.filter(
        Q(status=ComplianceCertificate.Status.VALID)
        | Q(status=ComplianceCertificate.Status.EXPIRING),
        expires_date__isnull=False,
        expires_date__lte=horizon,
    )
    return list(
        qs.values("number", "supplier__name", "requirement__name", "expires_date", "status")
    )
