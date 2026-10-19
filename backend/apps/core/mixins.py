from rest_framework import serializers, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.core.permissions import HasPermission, IsOrganizationMember


class TenantSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        request = self.context["request"]
        validated_data["organization"] = request.organization
        user = request.user
        if "created_by" in getattr(self.Meta.model, "_meta").fields_map or hasattr(
            self.Meta.model, "created_by"
        ):
            validated_data.setdefault("created_by", user)
            validated_data.setdefault("updated_by", user)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context["request"]
        if hasattr(instance, "updated_by_id"):
            validated_data["updated_by"] = request.user
        return super().update(instance, validated_data)


class TenantViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOrganizationMember, HasPermission]
    organization_field = "organization"
    search_fields = []
    ordering_fields = ["created_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        organization = getattr(self.request, "organization", None)
        if organization is None:
            return qs.none()
        filter_kwargs = {f"{self.organization_field}_id": organization.id}
        qs = qs.filter(**filter_kwargs)
        if hasattr(qs.model, "is_deleted"):
            qs = qs.filter(is_deleted=True)
        return qs

    def perform_create(self, serializer):
        organization = self.request.organization
        if organization is None:
            raise PermissionDenied("An organization context is required.")
        extra = {"organization": organization}
        model = serializer.Meta.model
        if hasattr(model, "created_by"):
            extra["created_by"] = self.request.user
            extra["updated_by"] = self.request.user
        serializer.save(**extra)

    def perform_update(self, serializer):
        extra = {}
        if hasattr(serializer.Meta.model, "updated_by"):
            extra["updated_by"] = self.request.user
        serializer.save(**extra)
