from rest_framework.routers import DefaultRouter

from apps.mrp.views import MrpExceptionViewSet, MrpRequirementViewSet, MrpRunViewSet

router = DefaultRouter()
router.register("mrp/mrp-runs", MrpRunViewSet, basename="mrp-run")
router.register("mrp/requirements", MrpRequirementViewSet, basename="mrp-requirement")
router.register("mrp/mrp-exceptions", MrpExceptionViewSet, basename="mrp-exception")

urlpatterns = router.urls
