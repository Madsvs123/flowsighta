from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.approvals.models import ApprovalDecision, ApprovalPolicy, ApprovalRequest, ApprovalStep
from apps.approvals.serializers import (
    ApprovalDecisionSerializer,
    ApprovalPolicySerializer,
    ApprovalRequestSerializer,
    ApprovalStepSerializer,
)
from apps.core.mixins import TenantViewSet


class ApprovalPolicyViewSet(TenantViewSet):
    queryset = ApprovalPolicy.objects.all()
    serializer_class = ApprovalPolicySerializer
    required_permission = "approvals.view"
    write_permission = "approvals.manage"
    search_fields = ["name", "object_type"]
    filterset_fields = ["object_type", "is_active"]


class ApprovalRequestViewSet(TenantViewSet):
    queryset = ApprovalRequest.objects.select_related("policy", "requested_by").prefetch_related("steps")
    serializer_class = ApprovalRequestSerializer
    required_permission = "approvals.view"
    write_permission = "approvals.manage"
    search_fields = ["reference", "object_id", "policy__name"]
    filterset_fields = ["status", "policy"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = dict(qs.values_list("status").annotate(count=Count("id")))
        pending_steps = ApprovalStep.objects.filter(
            request__organization=request.organization, status=ApprovalStep.Status.PENDING
        ).count()
        return Response(
            {
                "requests": qs.count(),
                "pending": by_status.get("pending", 0),
                "approved": by_status.get("approved", 0),
                "rejected": by_status.get("rejected", 0),
                "cancelled": by_status.get("cancelled", 0),
                "pending_steps": pending_steps,
                "policies": ApprovalPolicy.objects.filter(organization=request.organization, is_active=True).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        """Decide the request: body {approved: bool, comment: str}. Also decides
        the next pending step and records an ApprovalDecision."""
        approval = self.get_object()
        if approval.status != ApprovalRequest.Status.PENDING:
            return Response(self.get_serializer(approval).data)
        approved = bool(request.data.get("approved"))
        comment = request.data.get("comment", "")
        step = approval.steps.filter(status=ApprovalStep.Status.PENDING).order_by("sequence").first()
        if step is not None:
            step.status = ApprovalStep.Status.APPROVED if approved else ApprovalStep.Status.REJECTED
            step.comment = comment
            step.save(update_fields=["status", "comment", "updated_at"])
            ApprovalDecision.objects.create(
                organization=approval.organization,
                step=step,
                decision=ApprovalDecision.Decision.APPROVED if approved else ApprovalDecision.Decision.REJECTED,
                comment=comment,
                created_by=request.user,
                updated_by=request.user,
            )
        pending = approval.steps.filter(status=ApprovalStep.Status.PENDING).count()
        if pending != 0:
            approval.status = (
                ApprovalRequest.Status.APPROVED if approved else ApprovalRequest.Status.REJECTED
            )
            approval.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(approval).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        approval = self.get_object()
        approval.status = ApprovalRequest.Status.CANCELLED
        approval.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(approval).data)


class ApprovalStepViewSet(TenantViewSet):
    queryset = ApprovalStep.objects.select_related("request", "approver")
    serializer_class = ApprovalStepSerializer
    required_permission = "approvals.view"
    write_permission = "approvals.manage"
    filterset_fields = ["request", "approver", "status"]


class ApprovalDecisionViewSet(TenantViewSet):
    queryset = ApprovalDecision.objects.select_related("step", "step__approver")
    serializer_class = ApprovalDecisionSerializer
    required_permission = "approvals.view"
    write_permission = "approvals.manage"
    filterset_fields = ["step", "decision"]
