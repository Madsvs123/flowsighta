from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.warranty.models import (
    ClaimResolution,
    WarrantyClaim,
    WarrantyPlan,
    WarrantyRegistration,
)
from apps.warranty.serializers import (
    ClaimResolutionSerializer,
    WarrantyClaimSerializer,
    WarrantyPlanSerializer,
    WarrantyRegistrationSerializer,
)


class WarrantyPlanViewSet(TenantViewSet):
    queryset = WarrantyPlan.objects.select_related("product")
    serializer_class = WarrantyPlanSerializer
    required_permission = "warranty.view"
    write_permission = "warranty.manage"
    search_fields = ["product__sku", "product__name"]
    filterset_fields = ["product", "is_active"]


class WarrantyRegistrationViewSet(TenantViewSet):
    queryset = WarrantyRegistration.objects.select_related("product", "serial")
    serializer_class = WarrantyRegistrationSerializer
    required_permission = "warranty.view"
    write_permission = "warranty.manage"
    search_fields = ["customer_ref", "product__sku", "serial__serial"]
    filterset_fields = ["product", "serial", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        today = timezone.localdate()
        expiring = qs.filter(
            status=WarrantyRegistration.Status.ACTIVE,
            end_date__gte=today,
            end_date__lte=today + timezone.timedelta(days=30),
        ).count()
        claim_agg = WarrantyClaim.objects.filter(organization=request.organization).aggregate(
            total=Sum("resolutions__cost")
        )
        return Response(
            {
                "registrations": qs.count(),
                "active": qs.filter(status=WarrantyRegistration.Status.ACTIVE).count(),
                "expired": qs.filter(status=WarrantyRegistration.Status.EXPIRED).count(),
                "void": qs.filter(status=WarrantyRegistration.Status.VOID).count(),
                "expiring_30d": expiring,
                "open_claims": WarrantyClaim.objects.filter(
                    organization=request.organization,
                    status__in=[
                        WarrantyClaim.Status.OPEN,
                        WarrantyClaim.Status.UNDER_REVIEW,
                    ],
                ).count(),
                "resolution_cost": float(claim_agg["total"] or 0),
            }
        )

    @action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        registration = self.get_object()
        if registration.status != WarrantyRegistration.Status.ACTIVE:
            raise ValidationError("Only active registrations can be voided.")
        registration.status = WarrantyRegistration.Status.EXPIRED
        registration.updated_by = request.user
        registration.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(registration).data)


class WarrantyClaimViewSet(TenantViewSet):
    queryset = WarrantyClaim.objects.select_related("registration", "registration__product")
    serializer_class = WarrantyClaimSerializer
    required_permission = "warranty.view"
    write_permission = "warranty.manage"
    search_fields = ["registration__customer_ref", "description"]
    filterset_fields = ["registration", "status", "created_at"]

    @action(detail=True, methods=["post"])
    def start_review(self, request, pk=None):
        claim = self.get_object()
        if claim.status != WarrantyClaim.Status.OPEN:
            raise ValidationError("Only open claims can be moved to review.")
        claim.status = WarrantyClaim.Status.UNDER_REVIEW
        claim.updated_by = request.user
        claim.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(claim).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        claim = self.get_object()
        if claim.status not in (
            WarrantyClaim.Status.OPEN,
            WarrantyClaim.Status.UNDER_REVIEW,
        ):
            raise ValidationError("Only open or in-review claims can be approved.")
        claim.status = WarrantyClaim.Status.APPROVED
        claim.updated_by = request.user
        claim.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(claim).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        claim = self.get_object()
        if claim.status not in (
            WarrantyClaim.Status.OPEN,
            WarrantyClaim.Status.UNDER_REVIEW,
        ):
            raise ValidationError("Only open or in-review claims can be rejected.")
        claim.status = WarrantyClaim.Status.REJECTED
        claim.updated_by = request.user
        claim.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(claim).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        claim = self.get_object()
        if claim.status not in (
            WarrantyClaim.Status.APPROVED,
            WarrantyClaim.Status.REJECTED,
        ):
            raise ValidationError("Only approved or rejected claims can be closed.")
        claim.status = WarrantyClaim.Status.CLOSED
        claim.updated_by = request.user
        claim.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(claim).data)


class ClaimResolutionViewSet(TenantViewSet):
    queryset = ClaimResolution.objects.select_related("claim")
    serializer_class = ClaimResolutionSerializer
    required_permission = "warranty.view"
    write_permission = "warranty.manage"
    search_fields = ["notes", "claim__description"]
    filterset_fields = ["claim", "type"]
