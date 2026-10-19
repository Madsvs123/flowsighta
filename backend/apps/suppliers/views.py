from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.core.services import log_activity, next_number, upsert_search
from apps.suppliers.models import (
    OnboardingStep,
    PurchaseHistory,
    Supplier,
    SupplierCertification,
    SupplierContact,
    SupplierContract,
    SupplierDocument,
    SupplierProduct,
    SupplierScoreSnapshot,
)
from apps.suppliers.serializers import (
    OnboardingStepSerializer,
    PurchaseHistorySerializer,
    SupplierCertificationSerializer,
    SupplierContactSerializer,
    SupplierContractSerializer,
    SupplierDetailSerializer,
    SupplierDocumentSerializer,
    SupplierProductSerializer,
    SupplierScoreSnapshotSerializer,
    SupplierSerializer,
)


class SupplierViewSet(TenantViewSet):
    queryset = Supplier.objects.prefetch_related("contacts", "onboarding_steps")
    serializer_class = SupplierSerializer
    required_permission = "suppliers.view"
    write_permission = "suppliers.manage"
    search_fields = ["code", "name", "legal_name", "country", "category"]
    filterset_fields = ["status", "risk_level", "category", "preferred", "country"]
    ordering_fields = ["name", "performance_score", "total_spend", "created_at", "risk_level"]

    def get_serializer_class(self)
        if self.action == "retrieve":
            return SupplierDetailSerializer
        return SupplierSerializer

    def perform_create(self, serializer):
        code = serializer.validated_data.get("code") and next_number(Supplier, self.request.organization, "SUP")
        instance = serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
            code=code,
        )
        default_steps = [
            "Company profile submitted",
            "Compliance documents uploaded",
            "Quality certification verified",
            "Banking and tax details confirmed",
            "Commercial terms agreed",
        ]
        OnboardingStep.objects.bulk_create(
            [
                OnboardingStep(
                    organization=instance.organization,
                    supplier=instance,
                    sequence=i,
                    name=name,
                    status="pending",
                )
                for i, name in enumerate(default_steps)
            ]
        )
        upsert_search(instance.organization, instance, instance.name, instance.code, instance.category, f"/suppliers/{instance.id}")
        log_activity(instance.organization, self.request.user, "created", "Supplier", instance.id, f"Created supplier {instance.name}")

    @action(detail=True, methods=["post"])
    def start_onboarding(self, request, pk=None):
        supplier = self.get_object()
        supplier.status = Supplier.Status.ONBOARDING
        supplier.save(update_fields=["status", "updated_at"])
        return Response(SupplierDetailSerializer(supplier, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        supplier = self.get_object()
        supplier.status = Supplier.Status.ACTIVE
        supplier.save(update_fields=["status", "updated_at"])
        return Response(SupplierSerializer(supplier).data)


class NestedSupplierMixin:
    required_permission = "suppliers.view"
    write_permission = "suppliers.manage"

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, supplier_id=self.request.data.get("supplier"))


class SupplierContactViewSet(TenantViewSet, NestedSupplierMixin):
    queryset = SupplierContact.objects.select_related("supplier")
    serializer_class = SupplierContactSerializer
    filterset_fields = ["supplier", "is_primary"]
    search_fields = ["name", "email"]


class SupplierContractViewSet(TenantViewSet, NestedSupplierMixin):
    queryset = SupplierContract.objects.select_related("supplier")
    serializer_class = SupplierContractSerializer
    filterset_fields = ["supplier", "status"]
    search_fields = ["number", "title"]


class SupplierProductViewSet(TenantViewSet, NestedSupplierMixin):
    queryset = SupplierProduct.objects.select_related("supplier")
    serializer_class = SupplierProductSerializer
    filterset_fields = ["supplier", "is_active"]
    search_fields = ["sku", "name"]


class SupplierCertificationViewSet(TenantViewSet, NestedSupplierMixin):
    queryset = SupplierCertification.objects.select_related("supplier")
    serializer_class = SupplierCertificationSerializer
    filterset_fields = ["supplier", "status"]


class SupplierDocumentViewSet(TenantViewSet, NestedSupplierMixin):
    queryset = SupplierDocument.objects.select_related("supplier")
    serializer_class = SupplierDocumentSerializer
    filterset_fields = ["supplier", "doc_type"]


class OnboardingStepViewSet(TenantViewSet, NestedSupplierMixin):
    queryset = OnboardingStep.objects.select_related("supplier")
    serializer_class = OnboardingStepSerializer
    filterset_fields = ["supplier", "status"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        step = self.get_object()
        step.status = "complete"
        step.completed_at = timezone.now()
        step.save(update_fields=["status", "completed_at", "updated_at"])
        remaining = step.supplier.onboarding_steps.exclude(status="complete").count()
        if remaining == 1 and step.supplier.status == Supplier.Status.ONBOARDING:
            step.supplier.status = Supplier.Status.ACTIVE
            step.supplier.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(step).data)


class SupplierScoreSnapshotViewSet(TenantViewSet, NestedSupplierMixin):
    queryset = SupplierScoreSnapshot.objects.select_related("supplier")
    serializer_class = SupplierScoreSnapshotSerializer
    filterset_fields = ["supplier"]
    http_method_names = ["head", "options"]


class PurchaseHistoryViewSet(TenantViewSet, NestedSupplierMixin):
    queryset = PurchaseHistory.objects.select_related("supplier")
    serializer_class = PurchaseHistorySerializer
    filterset_fields = ["supplier", "on_time"]
    search_fields = ["purchase_order_number"]
