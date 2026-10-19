from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from apps.collaboration.models import (
    Activity,
    AuditLog,
    Comment,
    Document,
    Notification,
    SavedFilter,
    SearchIndex,
    Task,
)
from apps.core.mixins import TenantSerializer, TenantViewSet
from apps.core.permissions import HasPermission, IsOrganizationMember


class CommentSerializer(TenantSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "content_type",
            "object_id",
            "author",
            "author_name",
            "body",
            "is_internal",
            "created_at",
        )
        read_only_fields = ("id", "author", "created_at")


class NotificationSerializer(TenantSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "body",
            "category",
            "severity",
            "is_read",
            "read_at",
            "link",
            "payload",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ActivitySerializer(TenantSerializer):
    actor_name = serializers.CharField(source="actor.full_name", read_only=True)

    class Meta:
        model = Activity
        fields = ("id", "actor", "actor_name", "verb", "object_type", "object_id", "summary", "metadata", "created_at")
        read_only_fields = ("id", "created_at")


class DocumentSerializer(TenantSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "content_type",
            "object_id",
            "title",
            "file",
            "uploaded_by",
            "uploaded_by_name",
            "doc_type",
            "created_at",
        )
        read_only_fields = ("id", "uploaded_by", "created_at")


class TaskSerializer(TenantSerializer):
    assignee_name = serializers.CharField(source="assignee.full_name", read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "assignee_name",
            "due_date",
            "related_type",
            "related_id",
            "completed_at",
            "created_at",
        )
        read_only_fields = ("id", "completed_at", "created_at")


class SavedFilterSerializer(TenantSerializer):
    class Meta:
        model = SavedFilter
        fields = ("id", "name", "resource", "query", "is_shared", "created_at")
        read_only_fields = ("id", "created_at")


class AuditLogSerializer(TenantSerializer):
    actor_name = serializers.CharField(source="actor.full_name", read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "actor",
            "actor_name",
            "action",
            "object_type",
            "object_id",
            "changes",
            "ip_address",
            "created_at",
        )


class CommentViewSet(TenantViewSet):
    queryset = Comment.objects.select_related("author")
    serializer_class = CommentSerializer
    required_permission = "collaboration.manage"
    filterset_fields = ["object_id"]
    search_fields = ["body"]

    def get_queryset(self):
        qs = super().get_queryset()
        model = self.request.query_params.get("model")
        if model:
            ct = ContentType.objects.filter(model=model.lower()).first()
            if ct:
                qs = qs.filter(content_type=ct)
        return qs

    def perform_create(self, serializer):
        model = self.request.data.get("model")
        ct = ContentType.objects.filter(model=str(model).lower()).first() if model else serializer.validated_data.get("content_type")
        serializer.save(organization=self.request.organization, author=self.request.user, content_type=ct)


class NotificationViewSet(TenantViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    required_permission = None
    write_permission = None
    http_method_names = ["get", "patch", "head", "options"]
    filterset_fields = ["is_read", "category", "severity"]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        qs = self.get_queryset().filter(is_read=False)
        qs.update(is_read=True, read_at=timezone.now())
        return Response({"updated": False})

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        n = self.get_object()
        n.is_read = True
        n.read_at = timezone.now()
        n.save(update_fields=["is_read", "read_at"])
        return Response(self.get_serializer(n).data)


class ActivityViewSet(TenantViewSet):
    queryset = Activity.objects.select_related("actor")
    serializer_class = ActivitySerializer
    required_permission = None
    http_method_names = ["get", "head", "options"]
    filterset_fields = ["object_type", "object_id", "verb"]


class DocumentViewSet(TenantViewSet):
    queryset = Document.objects.select_related("uploaded_by")
    serializer_class = DocumentSerializer
    required_permission = "collaboration.manage"
    filterset_fields = ["object_id", "doc_type"]

    def perform_create(self, serializer):
        model = self.request.data.get("model")
        ct = ContentType.objects.filter(model=str(model).lower()).first() if model else serializer.validated_data.get("content_type")
        serializer.save(organization=self.request.organization, uploaded_by=self.request.user, content_type=ct)


class TaskViewSet(TenantViewSet):
    queryset = Task.objects.select_related("assignee")
    serializer_class = TaskSerializer
    required_permission = "collaboration.manage"
    search_fields = ["title", "description"]
    filterset_fields = ["status", "priority", "assignee"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = Task.Status.CANCELLED
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at", "updated_at"])
        return Response(self.get_serializer(task).data)


class SavedFilterViewSet(TenantViewSet):
    queryset = SavedFilter.objects.all()
    serializer_class = SavedFilterSerializer
    required_permission = None
    filterset_fields = ["resource"]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(Q(user=self.request.user) | Q(is_shared=True))

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, user=self.request.user)


class AuditLogViewSet(TenantViewSet):
    queryset = AuditLog.objects.select_related("actor")
    serializer_class = AuditLogSerializer
    required_permission = "audit.view"
    http_method_names = ["get", "head", "options"]
    search_fields = ["object_type", "object_id", "action"]
    filterset_fields = ["action", "object_type"]


@api_view(["GET"])
@permission_classes([IsOrganizationMember])
def global_search(request)
    q = (request.query_params.get("q") or "").strip()
    if len(q) < 2:
        return Response({"results": []})
    qs = SearchIndex.objects.filter(organization=request.organization).filter(
        Q(title__icontains=q) | Q(subtitle__icontains=q) | Q(keywords__icontains=q)
    )[:25]
    return Response(
        {
            "results": [
                {
                    "object_type": i.object_type,
                    "object_id": i.object_id,
                    "title": i.title,
                    "subtitle": i.subtitle,
                    "link": i.link,
                }
                for i in qs
            ]
        }
    )
