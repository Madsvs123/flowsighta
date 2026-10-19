from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.contracts.models import Contract, ContractClause, ContractMilestone
from apps.contracts.serializers import (
    ContractClauseSerializer,
    ContractMilestoneSerializer,
    ContractSerializer,
)
from apps.core.mixins import TenantViewSet


class ContractViewSet(TenantViewSet):
    queryset = Contract.objects.select_related("supplier")
    serializer_class = ContractSerializer
    required_permission = "contracts.view"
    write_permission = "contracts.manage"
    search_fields = ["number", "title", "supplier__name"]
    filterset_fields = ["supplier", "type", "status"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        milestones = ContractMilestone.objects.filter(organization=request.organization)
        clauses = ContractClause.objects.filter(organization=request.organization)
        return Response(
            {
                "contract_count": qs.count(),
                "active_contracts": qs.filter(status=Contract.Status.ACTIVE).count(),
                "draft_contracts": qs.filter(status=Contract.Status.DRAFT).count(),
                "expired_contracts": qs.filter(status=Contract.Status.EXPIRED).count(),
                "terminated_contracts": qs.filter(status=Contract.Status.TERMINATED).count(),
                "total_value": float(
                    qs.filter(status=Contract.Status.ACTIVE).aggregate(v=Sum("total_value"))["v"] or 0
                ),
                "clause_count": clauses.count(),
                "milestone_count": milestones.count(),
                "overdue_milestones": milestones.filter(status=ContractMilestone.Status.OVERDUE).count(),
                "by_type": {t: qs.filter(type=t).count() for t, _ in Contract.Status.choices},
                "upcoming_milestones": list(
                    milestones.filter(
                        status=ContractMilestone.Status.PENDING, due_date__isnull=False
                    )
                    .order_by("due_date")[:5]
                    .values("title", "due_date", "contract__number")
                ),
            }
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        contract = self.get_object()
        if contract.status not in (Contract.Status.DRAFT, Contract.Status.EXPIRED):
            return Response({"detail": "Only draft or expired contracts can be activated."}, status=400)
        contract.status = Contract.Status.ACTIVE
        if contract.start_date is None:
            contract.start_date = timezone.now().date()
        contract.save(update_fields=["status", "start_date", "updated_at"])
        return Response(self.get_serializer(contract).data)

    @action(detail=True, methods=["post"])
    def terminate(self, request, pk=None):
        contract = self.get_object()
        contract.status = Contract.Status.TERMINATED
        contract.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(contract).data)


class ContractClauseViewSet(TenantViewSet):
    queryset = ContractClause.objects.select_related("contract")
    serializer_class = ContractClauseSerializer
    required_permission = "contracts.view"
    write_permission = "contracts.manage"
    search_fields = ["title", "body", "contract__number"]
    filterset_fields = ["contract"]


class ContractMilestoneViewSet(TenantViewSet):
    queryset = ContractMilestone.objects.select_related("contract")
    serializer_class = ContractMilestoneSerializer
    required_permission = "contracts.view"
    write_permission = "contracts.manage"
    search_fields = ["title", "contract__number"]
    filterset_fields = ["contract", "status"]

    @action(detail=True, methods=["post"])
    def achieve(self, request, pk=None):
        milestone = self.get_object()
        milestone.status = ContractMilestone.Status.ACHIEVED
        milestone.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(milestone).data)
