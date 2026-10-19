from django.db.models import Count, Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.core.services import next_number
from apps.purchase_contracts.models import ContractRelease, PurchaseContract, PurchaseContractLine
from apps.purchase_contracts.serializers import (
    ContractReleaseSerializer,
    PurchaseContractLineSerializer,
    PurchaseContractSerializer,
)


class PurchaseContractViewSet(TenantViewSet):
    queryset = PurchaseContract.objects.select_related("supplier").prefetch_related("lines", "releases")
    serializer_class = PurchaseContractSerializer
    required_permission = "purchase_contracts.view"
    write_permission = "purchase_contracts.manage"
    search_fields = ["number", "title", "supplier__name"]
    filterset_fields = ["status", "supplier"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
            number=next_number(PurchaseContract, self.request.organization, "PC"),
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        releases = ContractRelease.objects.filter(contract__organization=request.organization)
        by_status = dict(qs.values_list("status").annotate(count=Count("id"))
        return Response(
            {
                "contracts": qs.count(),
                "active": by_status.get("active", 0),
                "draft": by_status.get("draft", 0),
                "expired": by_status.get("expired", 0),
                "terminated": by_status.get("terminated", 0),
                "total_value": qs.aggregate(total=Sum("total_value"))["total"] or 0,
                "releases": releases.count(),
                "released_quantity": releases.filter(status=ContractRelease.Status.ISSUED).aggregate(
                    total=Sum("quantity")
                )["total"]
                or 0,
            }
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        contract = self.get_object()
        contract.status = PurchaseContract.Status.ACTIVE
        contract.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(contract).data)

    @action(detail=True, methods=["post"])
    def terminate(self, request, pk=None):
        contract = self.get_object()
        contract.status = PurchaseContract.Status.TERMINATED
        contract.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(contract).data)


class PurchaseContractLineViewSet(TenantViewSet):
    queryset = PurchaseContractLine.objects.select_related("contract", "product")
    serializer_class = PurchaseContractLineSerializer
    required_permission = "purchase_contracts.view"
    write_permission = "purchase_contracts.manage"
    filterset_fields = ["contract", "product"]


class ContractReleaseViewSet(TenantViewSet):
    queryset = ContractRelease.objects.select_related("contract")
    serializer_class = ContractReleaseSerializer
    required_permission = "purchase_contracts.view"
    write_permission = "purchase_contracts.manage"
    search_fields = ["number"]
    filterset_fields = ["contract", "status"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            number=next_number(ContractRelease, self.request.organization, "REL"),
        )

    @action(detail=True, methods=["post"])
    def receive(self, request, pk=None):
        release = self.get_object()
        release.status = ContractRelease.Status.RECEIVED
        release.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(release).data)
