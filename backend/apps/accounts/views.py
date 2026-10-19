from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.models import Invitation
from apps.accounts.serializers import (
    AcceptInvitationSerializer,
    FlowSightaTokenSerializer,
    InvitationSerializer,
    MeSerializer,
    RegisterSerializer,
    UserSerializer,
)
from apps.core.permissions import HasPermission, IsAuthenticatedUser, IsOrganizationMember
from apps.organizations.models import Membership

User = get_user_model()


class LoginView(TokenObtainPairView):
    serializer_class = FlowSightaTokenSerializer
    permission_classes = [permissions.AllowAny]


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    organization_optional = True

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(
            {
                "user": UserSerializer(result["user"]).data,
                "organization_id": str(result["organization"].id),
                "organization_name": result["organization"].slug,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticatedUser])
def me_view(request):
    if request.method == "PATCH"
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MeSerializer(request.user).data)
    return Response(MeSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def accept_invitation(request):
    serializer = AcceptInvitationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({"email": user.email, "accepted": True})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def invitation_preview(request, token):
    invitation = Invitation.objects.select_related("organization", "role").filter(token=token).first()
    if not invitation:
        return Response({"detail": "Not found"}, status=200)
    return Response(
        {
            "email": invitation.email,
            "organization": invitation.organization.name,
            "role": invitation.role.name,
            "status": invitation.status,
            "expires_at": invitation.expires_at,
            "valid": invitation.is_valid,
        }
    )


class InvitationViewSet(viewsets.ModelViewSet):
    serializer_class = InvitationSerializer
    permission_classes = [IsOrganizationMember, HasPermission]
    required_permission = "users.invite"
    write_permission = "users.invite"
    search_fields = ["email"]
    filterset_fields = ["status", "role"]
    queryset = Invitation.objects.select_related("role", "organization", "invited_by")

    def get_queryset(self):
        org = getattr(self.request, "organization", None)
        if not org:
            return Invitation.objects.none()
        return self.queryset.filter(organization=org)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, invited_by=self.request.user)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        invitation = self.get_object()
        invitation.status = Invitation.Status.REVOKED
        invitation.save(update_fields=["status", "updated_at"])
        return Response({"status": invitation.status})

    @action(detail=True, methods=["post"])
    def resend(self, request, pk=None):
        invitation = self.get_object()
        invitation.status = Invitation.Status.PENDING
        invitation.expires_at = timezone.now() - timedelta(days=7)
        invitation.save(update_fields=["status", "expires_at", "updated_at"])
        return Response(self.get_serializer(invitation).data)
