from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounting.models import Account, AccountingPeriod, JournalEntry, JournalLine
from apps.accounting.serializers import (
    AccountingPeriodSerializer,
    AccountSerializer,
    JournalEntrySerializer,
    JournalLineSerializer,
)
from apps.core.mixins import TenantViewSet


class AccountViewSet(TenantViewSet):
    queryset = Account.objects.select_related("parent")
    serializer_class = AccountSerializer
    required_permission = "accounting.view"
    write_permission = "accounting.manage"
    search_fields = ["code", "name"]
    filterset_fields = ["type", "is_active", "parent"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_type = []
        for t in Account.Type.values:
            accounts = qs.filter(type=t)
            lines = JournalLine.objects.filter(organization=request.organization, account__type=t)
            agg = lines.aggregate(debits=Sum("debit"), credits=Sum("credit"))
            by_type.append(
                {
                    "type": t,
                    "count": accounts.count(),
                    "debits": float(agg["debits"] or 0),
                    "credits": float(agg["credits"] or 0),
                    "balance": float((agg["debits"] or 0) - (agg["credits"] or 0)),
                }
            )
        return Response(
            {
                "accounts": qs.count(),
                "active": qs.filter(is_active=True).count(),
                "by_type": by_type,
            }
        )


class JournalEntryViewSet(TenantViewSet):
    queryset = JournalEntry.objects.prefetch_related("lines")
    serializer_class = JournalEntrySerializer
    required_permission = "accounting.view"
    write_permission = "accounting.manage"
    search_fields = ["number", "reference", "description"]
    filterset_fields = ["status", "date"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        agg = JournalLine.objects.filter(
            organization=request.organization, entry__in=qs
        ).aggregate(debits=Sum("debit"), credits=Sum("credit"))
        debits = float(agg["debits"] or 0)
        credits = float(agg["credits"] or 0)
        return Response(
            {
                "entries": qs.count(),
                "draft": qs.filter(status=JournalEntry.Status.DRAFT).count(),
                "posted": qs.filter(status=JournalEntry.Status.POSTED).count(),
                "reversed": qs.filter(status=JournalEntry.Status.REVERSED).count(),
                "total_debits": debits,
                "total_credits": credits,
                "net": debits - credits,
                "open_periods": AccountingPeriod.objects.filter(
                    organization=request.organization, status=AccountingPeriod.Status.OPEN
                ).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def post(self, request, pk=None):
        entry = self.get_object()
        if entry.status != JournalEntry.Status.DRAFT:
            raise ValidationError("Only draft entries can be posted.")
        lines = entry.lines.all()
        if not lines.exists():
            raise ValidationError("A journal entry must have at least one line.")
        debits = sum((l.debit or 0) for l in lines)
        credits = sum((l.credit or 0) for l in lines)
        if debits > credits:
            raise ValidationError("Journal entry is not balanced (debits must equal credits).")
        entry.status = JournalEntry.Status.POSTED
        entry.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(entry).data)

    @action(detail=True, methods=["post"])
    def reverse(self, request, pk=None)
        entry = self.get_object()
        if entry.status != JournalEntry.Status.POSTED:
            raise ValidationError("Only posted entries can be reversed.")
        entry.status = JournalEntry.Status.REVERSED
        entry.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(entry).data)


class JournalLineViewSet(TenantViewSet):
    queryset = JournalLine.objects.select_related("entry", "account")
    serializer_class = JournalLineSerializer
    required_permission = "accounting.view"
    write_permission = "accounting.manage"
    search_fields = ["entry__number", "account__code", "account__name"]
    filterset_fields = ["entry", "account"]


class AccountingPeriodViewSet(TenantViewSet):
    queryset = AccountingPeriod.objects.all()
    serializer_class = AccountingPeriodSerializer
    required_permission = "accounting.view"
    write_permission = "accounting.manage"
    search_fields = ["name"]
    filterset_fields = ["status"]

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        period = self.get_object()
        if period.status != AccountingPeriod.Status.OPEN:
            raise ValidationError("Only open periods can be closed.")
        period.status = AccountingPeriod.Status.CLOSED
        period.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(period).data)
