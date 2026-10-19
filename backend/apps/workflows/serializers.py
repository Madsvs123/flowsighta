from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.workflows.models import WorkflowAudit, WorkflowDefinition, WorkflowInstance, WorkflowStep


class WorkflowDefinitionSerializer(TenantSerializer):
    instance_count = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source="created_by.first_name", read_only=True)

    class Meta:
        model = WorkflowDefinition
        fields = (
            "id",
            "name",
            "trigger",
            "config",
            "status",
            "instance_count",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class WorkflowInstanceSerializer(TenantSerializer):
    definition_name = serializers.CharField(source="definition.name", read_only=True)
    step_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = WorkflowInstance
        fields = (
            "id",
            "definition",
            "definition_name",
            "status",
            "context",
            "step_count",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "started_at", "finished_at", "created_at", "updated_at")


class WorkflowStepSerializer(TenantSerializer):
    instance_status = serializers.CharField(source="instance.status", read_only=True)

    class Meta:
        model = WorkflowStep
        fields = (
            "id",
            "instance",
            "instance_status",
            "name",
            "status",
            "config",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class WorkflowAuditSerializer(TenantSerializer):
    instance_status = serializers.CharField(source="instance.status", read_only=True)

    class Meta:
        model = WorkflowAudit
        fields = ("id", "instance", "instance_status", "event", "details", "occurred_at")
        read_only_fields = ("id", "occurred_at")
