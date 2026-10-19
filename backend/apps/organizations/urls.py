from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.organizations.views import (
    CustomerViewSet,
    LocationViewSet,
    MembershipViewSet,
    OrganizationViewSet,
    RegionViewSet,
    RoleViewSet,
    TeamViewSet,
    WarehouseViewSet,
)

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organizations")
router.register("regions", RegionViewSet, basename="regions")
router.register("teams", TeamViewSet, basename="teams")
router.register("roles", RoleViewSet, basename="roles")
router.register("memberships", MembershipViewSet, basename="memberships")
router.register("warehouses", WarehouseViewSet, basename="warehouses")
router.register("locations", LocationViewSet, basename="locations")
router.register("customers", CustomerViewSet, basename="customers")

urlpatterns = router.urls
