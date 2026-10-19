from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.document_control.models import (
    Document,
    DocumentApproval,
    DocumentLink,
    DocumentRevision,
)
from apps.document_control.serializers import (
    DocumentApprovalSerializer,
    DocumentLinkSerializer,
    DocumentRevisionSerializer,
    DocumentSerializer,
)


class DocumentViewSet(TenantViewSet):
    queryset = Document.objects.select_related("owner").prefetch_related("revisions")
    serializer_class = DocumentSerializer
    required_permission = "document_control.view"
    write_permission = "document_control.manage"
    search_fields = ["code", "title", "owner__email"]
    filterset_fields = ["type", "status", "owner"]

    @action(detail=False, methods=["get"])
    def summary(self, request)
        qs = self.get_queryset()
        by_type = {t: qs.filter(type=t).count() for t, _ in Document.Type.choices}
        by_status = {s: qs.filter(status=s).count() for s, _ in Document.Status.choices}
        revisions = DocumentRevision.objects.filter(organization=request.organization)
        pending_approvals = DocumentApproval.objects.filter(
            organization=request.organization
        ).count()
        recent = list(
            qs.order_by("created_at")[:5].values("code", "title", "type", "status")
        )
        return Response(
            {
                "document_count": qs.count(),
                "approved": by_status.get("approved", 0),
                "in_review": by_status.get("in_review", 0),
                "draft": by_status.get("draft", 0),
                "obsolete": by_status.get("obsolete", 0),
                "revision_count": revisions.count(),
                "approval_count": pending_approvals,
                "by_type": by_type,
                "by_status": by_status,
                "recent": recent,
            }
        )

    @action(detail=True, methods=["post"])
    def submit_for_review(self, request, pk=None):
        document = self.get_object()
        document.status = Document.Status.IN_REVIEW
        document.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(document).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        document = self.get_object()
        document.status = Document.Status.APPROVED
        document.save(update_fields=["status", "updated_at"])
        revision = document.revisions.first()
        if revision is not None and revision.approved_at is None:
            revision.approved_by = request.user
            revision.approved_at = timezone.now()
            revision.save(update_fields=["approved_by", "approved_at"])
        return Response(self.get_serializer(document).data)

    @action(detail=True, methods=["post"])
    def obsolete(self, request, pk=None):
        document = self.get_object()
        document.status = Document.Status.OBSOLETE
        document.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(document).data)


class DocumentRevisionViewSet(TenantViewSet):
    queryset = DocumentRevision.objects.select_related("document", "approved_by")
    serializer_class = DocumentRevisionSerializer
    required_permission = "document_control.view"
    write_permission = "document_control.manage"
    search_fields = ["document__code", "document__title", "version", "notes"]
    filterset_fields = ["document", "version"]


class DocumentApprovalViewSet(TenantViewSet):
    queryset = DocumentApproval.objects.select_related("revision", "revision__document", "approver")
    serializer_class = DocumentApprovalSerializer
    required_permission = "document_control.view"
    write_permission = "document_control.manage"
    search_fields = ["revision__document__code", "approver__email", "comment"]
    filterset_fields = ["revision", "approver", "decision"]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        approval = self.get_object()
        approval.decision = DocumentApproval.Decision.APPROVED
        approval.save(update_fields=["decision", "updated_at"])
        return Response(self.get_serializer(approval).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        approval = self.get_object()
        approval.decision = DocumentApproval.Decision.REJECTED
        approval.comment = request.data.get("comment", approval.comment)
        approval.save(update_fields=["decision", "comment", "updated_at"])
        return Response(self.get_serializer(approval).data)


class DocumentLinkViewSet(TenantViewSet):
    queryset = DocumentLink.objects.select_related("document")
    serializer_class = DocumentLinkSerializer
    required_permission = "document_control.view"
    write_permission = "document_control.manage"
    search_fields = ["document__code", "document__title", "object_type", "object_id"]
    filterset_fields = ["document", "object_type"]
