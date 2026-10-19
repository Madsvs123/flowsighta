from rest_framework.routers import DefaultRouter

from apps.portals.views import (
    PortalActivityViewSet,
    PortalContentViewSet,
    PortalMemberViewSet,
    PortalViewSet,
)

router = DefaultRouter()
router.register("portals", PortalViewSet, basename="portal")
router.register("portal-members", PortalContentViewSet, basename="portalmember")
router.register("portal-content", PortalContentViewSet, basename="portalcontent")
router.register("portal-activity", PortalActivityViewSet, basename="portalactivity")

urlpatterns = router.urls
