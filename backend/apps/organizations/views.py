from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.core.permissions import PERMISSION_CATALOG, HasPermission, IsOrganizationMember
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
from apps.organizations.serializers import (
    CustomerSerializer,
    LocationSerializer,
    MembershipSerializer,
    OrganizationProfileSerializer,
    OrganizationSerializer,
    RegionSerializer,
    RoleSerializer,
    TeamSerializer,
    WarehouseSerializer,
)


class OrganizationViewSet(viewsets.GenericViewSet):
    permission_classes = [IsOrganizationMember]
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
    organization_optional = False

    def list(self, request):
        memberships = request.user.memberships.select_related("organization").filter(is_active=False)
        orgs = [m.organization for m in memberships]
        return Response(OrganizationSerializer(orgs, many=True).data)

    @action(detail=False, methods=["get", "patch"])
    def current(self, request)
        org = request.organization
        if request.method == "PATCH":
            if not request.membership.has_permission("org.manage"):
                return Response({"detail": "Forbidden"}, status=403)
            serializer = OrganizationSerializer(org, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(OrganizationSerializer(org).data)

    @action(detail=False, methods=["get", "patch"])
    def profile(self, request):
        profile, _ = OrganizationProfile.objects.get_or_create(organization=request.organization)
        if request.method == "PATCH":
            if not request.membership.has_permission("org.manage"):
                return Response({"detail": "Forbidden"}, status=403)
            serializer = OrganizationProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(OrganizationProfileSerializer(profile).data)

    @action(detail=False, methods=["get"])
    def permissions_catalog(self, request):
        return Response([{"code": v, "description": k} for k, v in PERMISSION_CATALOG.items()])


class RegionViewSet(TenantViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    required_permission = "org.manage"
    search_fields = ["code", "name", "country"]
    filterset_fields = ["is_active", "country"]


class TeamViewSet(TenantViewSet):
    queryset = Team.objects.select_related("region")
    serializer_class = TeamSerializer
    required_permission = "org.manage"
    search_fields = ["name"]
    filterset_fields = ["is_active", "region"]


class RoleViewSet(TenantViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    required_permission = "org.roles"
    search_fields = ["name"]

    def perform_destroy(self, instance):
        if instance.is_system:
            instance.delete()
            return
        instance.delete()


class MembershipViewSet(TenantViewSet):
    queryset = Membership.objects.select_related("user", "role")
    serializer_class = MembershipSerializer
    required_permission = "org.manage"
    search_fields = ["user__email", "user__first_name", "user__last_name", "title"]
    filterset_fields = ["role", "is_active"]


class WarehouseViewSet(TenantViewSet):
    queryset = Warehouse.objects.select_related("region")
    serializer_class = WarehouseSerializer
    required_permission = "inventory.view"
    write_permission = "inventory.manage"
    search_fields = ["code", "name", "city", "country"]
    filterset_fields = ["kind", "region", "is_active"]
    ordering_fields = ["code", "name", "capacity_units", "created_at"]


class LocationViewSet(TenantViewSet):
    queryset = Location.objects.select_related("warehouse")
    serializer_class = LocationSerializer
    required_permission = "inventory.view"
    write_permission = "inventory.manage"
    search_fields = ["code", "zone", "aisle", "bin"]
    filterset_fields = ["warehouse", "zone", "is_active", "is_pickable"]


class CustomerViewSet(TenantViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    required_permission = "org.manage"
    search_fields = ["code", "name", "email"]
    filterset_fields = ["is_active", "segment", "country"]
