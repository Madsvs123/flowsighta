from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.organizations.models import (
    Customer,
    Location,
    Membership,
    Organization,
    OrganizationProfile,
    Region,
    Role,
    Team,
    Warehouse,
)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "slug",
            "org_type",
            "industry",
            "website",
            "tax_id",
            "logo",
            "timezone",
            "currency",
            "is_active",
            "settings",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "updated_at")


class OrganizationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationProfile
        fields = "__all__"
        read_only_fields = ("id", "organization", "created_at", "updated_at")


class RegionSerializer(TenantSerializer):
    class Meta:
        model = Region
        fields = ("id", "code", "name", "country", "timezone", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class TeamSerializer(TenantSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)
    member_count = serializers.IntegerField(source="members.count", read_only=True)

    class Meta:
        model = Team
        fields = ("id", "name", "description", "region", "region_name", "is_active", "member_count", "created_at")
        read_only_fields = ("id", "created_at")


class RoleSerializer(TenantSerializer):
    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "permissions",
            "is_system",
            "warehouse_scope",
            "region_scope",
            "created_at",
        )
        read_only_fields = ("id", "is_system", "created_at")


class MembershipSerializer(TenantSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    role_permissions = serializers.JSONField(source="role.permissions", read_only=True)

    class Meta:
        model = Membership
        fields = (
            "id",
            "user",
            "user_email",
            "user_name",
            "role",
            "role_name",
            "role_permissions",
            "teams",
            "is_active",
            "is_default",
            "title",
            "operational_access",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class WarehouseSerializer(TenantSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)
    capacity_utilization = serializers.ReadOnlyField()

    class Meta:
        model = Warehouse
        fields = (
            "id",
            "code",
            "name",
            "kind",
            "region",
            "region_name",
            "address_line1",
            "city",
            "state",
            "country",
            "postal_code",
            "latitude",
            "longitude",
            "capacity_units",
            "used_capacity_units",
            "capacity_utilization",
            "timezone",
            "is_active",
            "manager_email_address",
            "operating_days",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class LocationSerializer(TenantSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = Location
        fields = (
            "id",
            "warehouse",
            "warehouse_name",
            "code",
            "zone",
            "aisle",
            "location_type",
            "is_pickable",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CustomerSerializer(TenantSerializer):
    class Meta:
        model = Customer
        fields = (
            "id",
            "code",
            "name",
            "segment",
            "country",
            "city",
            "email",
            "phone",
            "payment_terms",
            "credit_limit",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
