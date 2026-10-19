from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class OrganizationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.organization = None
        request.membership = None
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return
        org_id = request.META.get(settings.ORGANIZATION_HEADER) or request.GET.get("org_id")
        if not org_id:
            membership = user.memberships.select_related("organization", "role").filter(is_active=True).first()
            if membership:
                request.organization = membership.organization_id
                request.membership = membership
            return
        membership = (
            user.memberships.select_related("organization", "role")
            .filter(organization_id=org_id, is_active=True)
            .first()
        )
        if membership:
            request.organization = membership.organization
            request.membership = membership


class AuditRequestMiddleware(MiddlewareMixin):
    def process_request(self, request)
        request.audit_ip = request.META.get("REMOTE_ADDR")
        request.audit_user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
