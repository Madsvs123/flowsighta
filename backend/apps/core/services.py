from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.collaboration.models import Activity, AuditLog, Notification, SearchIndex
from apps.core.realtime import publish_organization_event


def log_activity(organization, actor, verb, object_type, object_id, summary, metadata=None)
    Activity.objects.create(
        organization=organization,
        actor=actor,
        verb=verb,
        object_type=object_type,
        object_id=str(object_id) if object_id else "",
        summary=summary,
        metadata=metadata or {},
    )
    publish_organization_event(
        organization.id,
        "activity",
        {"verb": verb, "summary": summary, "object_type": object_type, "object_id": str(object_id) if object_id else ""},
    )


def write_audit(request, action, instance, changes=None):
    org = getattr(request, "organization", None)
    if org is None:
        return
    AuditLog.objects.create(
        organization=org,
        actor=getattr(request, "user", None) if getattr(request.user, "is_authenticated", False) else None,
        action=action,
        object_type=instance.__class__.__name__,
        object_id=str(getattr(instance, "pk", "")),
        changes=changes or {},
        ip_address=getattr(request, "audit_ip", None),
        user_agent=getattr(request, "audit_user_agent", ""),
    )


def notify_user(organization, user, title, body="", category="system", severity="info", link="", payload=None):
    notification = Notification.objects.create(
        organization=organization,
        user=user,
        title=title,
        body=body,
        category=category,
        severity=severity,
        link=link,
        payload=payload or {},
    )
    publish_organization_event(
        organization.id,
        "notification",
        {
            "id": str(notification.id),
            "user_id": str(user.id),
            "title": title,
            "severity": severity,
            "category": category,
        },
    )
    return notification


def upsert_search(organization, instance, title, subtitle="", keywords="", link=""):
    SearchIndex.objects.update_or_create(
        organization=organization,
        object_type=instance.__class__.__name__,
        object_id=str(instance.id),
        defaults={"title": title, "subtitle": subtitle, "keywords": keywords, "link": link},
    )


def next_number(model, organization, prefix):
    year = timezone.now().year
    count = model.objects.filter(organization=organization, created_at__year=year).count()
    return f"{prefix}-{year}-{count:05d}"
