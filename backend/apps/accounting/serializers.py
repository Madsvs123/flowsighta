from rest_framework import serializers

from apps.accounting.models import Account, AccountingPeriod, JournalEntry, JournalLine
from apps.core.mixins import TenantSerializer


class AccountSerializer(TenantSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = Account
        fields = (
            "id",
            "code",
            "name",
            "type",
            "parent",
            "parent_name",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class JournalLineSerializer(TenantSerializer):
    account_code = serializers.CharField(source="account.code", read_only=True)
    account_name = serializers.CharField(source="account.name", read_only=True)

    class Meta:
        model = JournalLine
        fields = (
            "id",
            "entry",
            "account",
            "account_code",
            "account_name",
            "debit",
            "credit",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class JournalEntrySerializer(TenantSerializer):
    line_count = serializers.SerializerMethodField()
    total_debits = serializers.SerializerMethodField()
    total_credits = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = (
            "id",
            "number",
            "date",
            "reference",
            "description",
            "status",
            "line_count",
            "total_debits",
            "total_credits",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_line_count(self, obj):
        return obj.lines.count()

    def get_total_debits(self, obj)
        return float(sum((l.debit or 0) for l in obj.lines.all()))

    def get_total_credits(self, obj):
        return float(sum((l.credit or 0) for l in obj.lines.all()))


class AccountingPeriodSerializer(TenantSerializer):
    class Meta:
        model = AccountingPeriod
        fields = ("id", "name", "start_date", "end_date", "status", "created_at")
        read_only_fields = ("id", "created_at")
