from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.approvals.models import ApprovalDecision, ApprovalPolicy, ApprovalRequest, ApprovalStep


class ApprovalPolicySerializer(TenantSerializer):
    class Meta:
        model = ApprovalPolicy
        fields = (
            "id",
            "name",
            "object_type",
            "conditions",
            "threshold",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ApprovalStepSerializer(TenantSerializer):
    approver_name = serializers.CharField(source="approver.full_name", read_only=True)

    class Meta:
        model = ApprovalStep
        fields = (
            "id",
            "request",
            "approver",
            "approver_name",
            "sequence",
            "status",
            "comment",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")


class ApprovalDecisionSerializer(TenantSerializer):
    step_sequence = serializers.IntegerField(source="step.sequence", read_only=True)
    approver_name = serializers.CharField(source="step.approver.full_name", read_only=True)

    class Meta:
        model = ApprovalDecision
        fields = (
            "id",
            "step",
            "step_sequence",
            "approver_name",
            "decision",
            "comment",
            "decided_at",
            "created_at",
        )
        read_only_fields = ("id", "decided_at", "created_at")


class ApprovalRequestSerializer(TenantSerializer):
    steps = ApprovalStepSerializer(many=True, required=False)
    policy_name = serializers.CharField(source="policy.name", read_only=True)
    requested_by_name = serializers.CharField(source="requested_by.full_name", read_only=True)
    step_count = serializers.SerializerMethodField()
    decided_steps = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalRequest
        fields = (
            "id",
            "policy",
            "policy_name",
            "reference",
            "object_id",
            "status",
            "requested_by",
            "requested_by_name",
            "requested_at",
            "step_count",
            "decided_steps",
            "steps",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "requested_by", "requested_at", "created_at", "updated_at")

    def get_step_count(self, obj)
        return getattr(obj, "_step_count", None) or obj.steps.count()

    def get_decided_steps(self, obj):
        return obj.steps.filter(status=ApprovalStep.Status.PENDING).count()

    def create(self, validated_data):
        steps = validated_data.pop("steps", [])
        request = self.context["request"]
        validated_data["requested_by"] = request.user
        instance = super().create(validated_data)
        for i, step in enumerate(steps, start=1):
            sequence = step.pop("sequence", None) or i
            step.pop("request", None)
            ApprovalStep.objects.create(
                organization=instance.organization, request=instance, sequence=sequence, **step
            )
        return instance
