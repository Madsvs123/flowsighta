from rest_framework import serializers

from apps.contracts.models import Contract, ContractClause, ContractMilestone
from apps.core.mixins import TenantSerializer


class ContractSerializer(TenantSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    supplier_code = serializers.CharField(source="supplier.code", read_only=True)
    clause_count = serializers.IntegerField(source="clauses.count", read_only=True)
    milestone_count = serializers.IntegerField(source="milestones.count", read_only=True)

    class Meta:
        model = Contract
        fields = (
            "id",
            "number",
            "supplier",
            "supplier_name",
            "supplier_code",
            "title",
            "type",
            "status",
            "start_date",
            "end_date",
            "total_value",
            "currency",
            "clause_count",
            "milestone_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ContractClauseSerializer(TenantSerializer):
    contract_number = serializers.CharField(source="contract.number", read_only=True)

    class Meta:
        model = ContractClause
        fields = (
            "id",
            "contract",
            "contract_number",
            "title",
            "sort_order",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ContractMilestoneSerializer(TenantSerializer):
    contract_number = serializers.CharField(source="contract.number", read_only=True)

    class Meta:
        model = ContractMilestone
        fields = (
            "id",
            "contract",
            "contract_number",
            "title",
            "due_date",
            "status",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
