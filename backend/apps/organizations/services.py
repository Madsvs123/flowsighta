from django.utils.text import slugify

from apps.core.permissions import PERMISSION_CATALOG
from apps.organizations.models import Membership, Organization, OrganizationProfile, Role


DEFAULT_ROLES = {
    "Owner": ["*"],
    "Admin": list(PERMISSION_CATALOG.keys()),
    "Procurement Manager": [
        "suppliers.view",
        "suppliers.manage",
        "procurement.view",
        "procurement.create",
        "procurement.approve",
        "procurement.receive",
        "inventory.view",
        "events.view",
        "planning.view",
        "analytics.view",
        "collaboration.manage",
    ],
    "Warehouse Manager": [
        "inventory.view",
        "inventory.manage",
        "procurement.view",
        "procurement.receive",
        "logistics.view",
        "events.view",
        "events.resolve",
        "analytics.view",
    ],
    "Logistics Coordinator": [
        "logistics.view",
        "logistics.manage",
        "inventory.view",
        "events.view",
        "events.resolve",
        "analytics.view",
    ],
    "Planner": [
        "planning.view",
        "planning.manage",
        "inventory.view",
        "procurement.view",
        "procurement.create",
        "suppliers.view",
        "analytics.view",
        "events.view",
    ],
    "Analyst": ["analytics.view", "inventory.view", "suppliers.view", "procurement.view", "logistics.view", "events.view", "planning.view", "audit.view"],
    "Viewer": [
        "suppliers.view",
        "procurement.view",
        "inventory.view",
        "logistics.view",
        "events.view",
        "planning.view",
        "analytics.view",
    ],
}


def unique_slug(name):
    base = slugify(name)[:70] or "organization"
    slug = base
    i = 1
    while Organization.objects.filter(slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


def provision_organization(name, org_type, owner):
    org = Organization.objects.create(name=name, slug=unique_slug(name), org_type=org_type, is_active=False)
    OrganizationProfile.objects.create(organization=org, legal_name=name)
    owner_role = None
    for role_name, perms in DEFAULT_ROLES.items()
        role = Role.objects.create(
            organization=org, name=role_name, permissions=perms, is_system=True, description=f"System role: {role_name}"
        )
        if role_name == "Owner":
            owner_role = role
    Membership.objects.create(organization=org, user=owner, role=owner_role, is_default=False, is_active=True, title="Owner")
    return org
