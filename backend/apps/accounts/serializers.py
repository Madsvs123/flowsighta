from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import Invitation
from apps.organizations.models import Membership, Organization, OrganizationProfile, Role

User = get_user_model()


class FlowSightaTokenSerializer(TokenObtainPairSerializer)
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["name"] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        self.user.last_login_at = timezone.now()
        self.user.save(update_fields=["last_login_at"])
        data["user"] = UserSerializer(self.user).data
        memberships = (
            Membership.objects.select_related("organization", "role")
            .filter(user=self.user, is_active=True)
        )
        data["memberships"] = MembershipBriefSerializer(memberships, many=True).data
        return data


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "job_title",
            "timezone",
            "avatar",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "email", "is_active", "created_at", "timezone")


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=120)
    last_name = serializers.CharField(max_length=120)
    organization_name = serializers.CharField(max_length=200)
    org_type = serializers.CharField(required=False, default="manufacturer")
    job_title = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        from apps.organizations.services import provision_organization

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            job_title=validated_data.get("job_title", ""),
        )
        org = provision_organization(
            name=validated_data["organization_name"],
            org_type=validated_data.get("org_type", "manufacturer"),
            owner=user,
        )
        return {"user": user, "organization": org}


class InvitationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    invited_by_name = serializers.CharField(source="invited_by.full_name", read_only=True)

    class Meta:
        model = Invitation
        fields = (
            "id",
            "email",
            "role",
            "role_name",
            "team",
            "status",
            "token",
            "expires_at",
            "accepted_at",
            "message",
            "organization_name",
            "invited_by_name",
            "created_at",
        )
        read_only_fields = ("id", "token", "status", "expires_at", "accepted_at", "created_at")


class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=10, required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    def validate(self, attrs):
        try:
            invitation = Invitation.objects.select_related("organization", "role").get(token=attrs["token"])
        except Invitation.DoesNotExist:
            raise serializers.ValidationError("Invitation is invalid.")
        if not invitation.is_valid:
            raise serializers.ValidationError("Invitation is no longer valid.")
        attrs["invitation"] = invitation
        return attrs

    def save(self, **kwargs):
        invitation = self.validated_data["invitation"]
        user = User.objects.filter(email__iexact=invitation.email).first()
        if user is None:
            user = User.objects.create_user(
                email=invitation.email,
                password=self.validated_data["password"],
                first_name=self.validated_data.get("first_name", invitation.email.split("@")[0]),
                last_name=self.validated_data.get("last_name", ""),
            )
        Membership.objects.get_or_create(
            organization=invitation.organization,
            user=user,
            defaults={"role": invitation.role, "is_default": False},
        )
        invitation.status = Invitation.Status.ACCEPTED
        invitation.accepted_at = timezone.now()
        invitation.save(update_fields=["status", "accepted_at"])
        return user


class MembershipBriefSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    organization_slug = serializers.CharField(source="organization.slug", read_only=True)
    org_type = serializers.CharField(source="organization.org_type", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    permissions = serializers.JSONField(source="role.permissions", read_only=True)
    currency = serializers.CharField(source="organization.currency", read_only=True)

    class Meta:
        model = Membership
        fields = (
            "id",
            "organization",
            "organization_name",
            "organization_slug",
            "org_type",
            "role",
            "role_name",
            "permissions",
            "is_default",
            "title",
            "operational_access",
            "currency",
        )


class MeSerializer(serializers.Serializer):
    def to_representation(self, user):
        memberships = Membership.objects.select_related("organization", "role").filter(user=user, is_active=True)
        return {
            "user": UserSerializer(user, context=self.context).data,
            "memberships": MembershipBriefSerializer(memberships, many=True).data,
        }
