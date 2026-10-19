from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.workflows.models import WorkflowAudit, WorkflowDefinition, WorkflowInstance, WorkflowStep
from apps.workflows.serializers import (
    WorkflowAuditSerializer,
    WorkflowDefinitionSerializer,
    WorkflowInstanceSerializer,
    WorkflowStepSerializer,
)


class WorkflowDefinitionViewSet(TenantViewSet):
    queryset = WorkflowDefinition.objects.select_related("created_by").annotate(
        instance_count=Count("instances", distinct=True)
    )
    serializer_class = WorkflowDefinitionSerializer
    required_permission = "workflows.view"
    write_permission = "workflows.manage"
    search_fields = ["name", "trigger"]
    filterset_fields = ["status", "trigger"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        definitions = self.get_queryset()
        instances = WorkflowInstance.objects.filter(organization=request.organization)
        steps = WorkflowStep.objects.filter(organization=request.organization)
        return Response(
            {
                "definition_count": definitions.count(),
                "active_definitions": definitions.filter(status=WorkflowDefinition.Status.ACTIVE).count(),
                "draft_definitions": definitions.filter(status=WorkflowDefinition.Status.DRAFT).count(),
                "inactive_definitions": definitions.filter(status=WorkflowDefinition.Status.INACTIVE).count(),
                "instance_count": instances.count(),
                "running_instances": instances.filter(status=WorkflowInstance.Status.RUNNING).count(),
                "completed_instances": instances.filter(status=WorkflowInstance.Status.COMPLETED).count(),
                "failed_instances": instances.filter(status=WorkflowInstance.Status.FAILED).count(),
                "cancelled_instances": instances.filter(status=WorkflowInstance.Status.CANCELLED).count(),
                "step_count": steps.count(),
                "completed_steps": steps.filter(status=WorkflowStep.Status.COMPLETED).count(),
                "audit_event_count": WorkflowAudit.objects.filter(organization=request.organization).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        definition = self.get_object()
        definition.status = WorkflowDefinition.Status.ACTIVE
        definition.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(definition).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        definition = self.get_object()
        definition.status = WorkflowDefinition.Status.INACTIVE
        definition.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(definition).data)


class WorkflowInstanceViewSet(TenantViewSet):
    queryset = WorkflowInstance.objects.select_related("definition").annotate(
        step_count=Count("steps", distinct=True)
    )
    serializer_class = WorkflowInstanceSerializer
    required_permission = "workflows.view"
    write_permission = "workflows.manage"
    search_fields = ["definition__name"]
    filterset_fields = ["definition", "status"]

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        instance = self.get_object()
        if instance.status not in (WorkflowInstance.Status.RUNNING,):
            return Response({"detail": "Only running instances can be cancelled"}, status=400)
        instance.status = WorkflowInstance.Status.CANCELLED
        instance.finished_at = timezone.now()
        instance.save(update_fields=["status", "updated_at"])
        WorkflowAudit.objects.create(
            organization=instance.organization,
            instance=instance,
            event="canceled",
            details={"by": request.user.email},
        )
        return Response(self.get_serializer(instance).data)


class WorkflowStepViewSet(TenantViewSet):
    queryset = WorkflowStep.objects.select_related("instance")
    serializer_class = WorkflowStepSerializer
    required_permission = "workflows.view"
    write_permission = "workflows.manage"
    search_fields = ["name", "instance__definition__name"]
    filterset_fields = ["instance", "status"]


class WorkflowAuditViewSet(TenantViewSet):
    queryset = WorkflowAudit.objects.select_related("instance")
    serializer_class = WorkflowAuditSerializer
    required_permission = "workflows.view"
    write_permission = "workflows.manage"
    http_method_names = ["get", "head", "options"]
    search_fields = ["event", "instance__definition__name"]
    filterset_fields = ["instance", "event"]
