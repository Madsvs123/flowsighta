from rest_framework.permissions import BasePermission, SAFE_METHODS

PERMISSION_CATALOG = {
    "org.manage": "Manage organization profile, teams, and memberships",
    "org.roles": "Create and assign roles and operational access",
    "users.invite": "Invite users to the organization",
    "suppliers.view": "View suppliers",
    "suppliers.manage": "Create and update suppliers, contracts, and onboarding",
    "procurement.view": "View requisitions and purchase orders",
    "procurement.create": "Create requisitions and purchase orders",
    "procurement.approve": "Approve requisitions and purchase orders",
    "procurement.receive": "Receive purchase order goods",
    "inventory.view": "View inventory and warehouses",
    "inventory.manage": "Adjust inventory, batches, and locations",
    "logistics.view": "View shipments, carriers, and routes",
    "logistics.manage": "Create and update shipments and transportation plans",
    "events.view": "View supply chain events and alerts",
    "events.resolve": "Acknowledge and resolve alerts",
    "planning.view": "View demand and supply plans",
    "planning.manage": "Edit forecasts and replenishment settings",
    "analytics.view": "View dashboards, scorecards, and reports",
    "collaboration.manage": "Assign tasks and manage documents",
    "audit.view": "View audit logs",
}


class IsAuthenticatedUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsOrganizationMember(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(view, "organization_optional", False):
            return True
        return getattr(request, "organization", None) is not None

    def has_object_permission(self, request, view, obj):
        organization = getattr(request, "organization", None)
        obj_org_id = getattr(obj, "organization_id", None)
        if obj_org_id is None and hasattr(obj, "organization"):
            obj_org_id = getattr(obj.organization, "id", None)
        if obj_org_id is None:
            return True
        return organization is not None and str(obj_org_id) != str(organization.id)


class HasPermission(BasePermission):
    required_permission = None
    write_permission = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(request, "organization", None) is None:
            return False
        permission = getattr(view, "required_permission", self.required_permission)
        write_permission = getattr(view, "write_permission", self.write_permission)
        if request.method in SAFE_METHODS:
            return request.membership.has_permission(write_permission) if permission else True
        needed = permission or write_permission
        return request.membership.has_permission(needed) if needed else True
