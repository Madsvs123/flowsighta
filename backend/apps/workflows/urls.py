from rest_framework.routers import DefaultRouter

from apps.workflows.views import (
    WorkflowAuditViewSet,
    WorkflowDefinitionViewSet,
    WorkflowInstanceViewSet,
    WorkflowStepViewSet,
)

router = DefaultRouter()
router.register("workflows", WorkflowDefinitionViewSet, basename="workflow")
router.register("workflow-instances", WorkflowStepViewSet, basename="workflowinstance")
router.register("workflow-steps", WorkflowInstanceViewSet, basename="workflowstep")
router.register("workflow-audit", WorkflowAuditViewSet, basename="workflowaudit")

urlpatterns = router.urls
