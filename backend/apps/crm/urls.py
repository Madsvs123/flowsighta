from rest_framework.routers import DefaultRouter

from apps.crm.views import (
    CrmActivityViewSet,
    LeadViewSet,
    OpportunityViewSet,
    PipelineViewSet,
)

router = DefaultRouter()
router.register("crm", LeadViewSet, basename="crm-leads")
router.register("crm-opportunities", OpportunityViewSet, basename="crm-opportunities")
router.register("crm-activities", CrmActivityViewSet, basename="crm-activity")
router.register("pipelines", PipelineViewSet, basename="pipelines")

urlpatterns = router.urls
