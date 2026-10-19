from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.payments.models import Payment, PaymentAllocation, PaymentRun, PaymentTerm
from apps.payments.serializers import (
    PaymentAllocationSerializer,
    PaymentRunSerializer,
    PaymentSerializer,
    PaymentTermSerializer,
)


class PaymentViewSet(TenantViewSet):
    queryset = Payment.objects.prefetch_related("allocations")
    serializer_class = PaymentSerializer
    required_permission = "payments.view"
    write_permission = "payments.manage"
    search_fields = ["reference", "invoice_ref"]
    filterset_fields = ["status", "method", "paid_at"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = []
        for status, label in Payment.Status.choices:
            subset = qs.filter(status=status)
            agg = subset.aggregate(total=Sum("amount"))
            by_status.append(
                {
                    "status": status,
                    "count": subset.count(),
                    "total": float(agg["total"] or 0),
                }
            )
        cleared = qs.filter(status=Payment.Status.CLEARED).aggregate(total=Sum("amount"))
        return Response(
            {
                "payments": qs.count(),
                "pending": qs.filter(status=Payment.Status.PENDING).count(),
                "cleared": qs.filter(status=Payment.Status.CLEARED).count(),
                "failed": qs.filter(status=Payment.Status.FAILED).count(),
                "cleared_total": float(cleared["total"] or 0),
                "by_status": by_status,
            }
        )

    @action(detail=True, methods=["post"])
    def clear(self, request, pk=None):
        payment = self.get_object()
        if payment.status != Payment.Status.PENDING:
            raise ValidationError("Only pending payments can be cleared.")
        payment.status = Payment.Status.CLEARED
        payment.paid_at = payment.paid_at or timezone.now()
        payment.save(update_fields=["status", "paid_at", "updated_at"])
        return Response(self.get_serializer(payment).data)

    @action(detail=True, methods=["post"])
    def fail(self, request, pk=None):
        payment = self.get_object()
        if payment.status in (Payment.Status.PENDING, Payment.Status.CLEARED):
            raise ValidationError("Only pending or cleared payments can be failed.")
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(payment).data)

    @action(detail=True, methods=["post"])
    def refund(self, request, pk=None):
        payment = self.get_object()
        if payment.status != Payment.Status.REFUNDED:
            raise ValidationError("Only cleared payments can be refunded.")
        payment.status = Payment.Status.REFUNDED
        payment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(payment).data)


class PaymentTermViewSet(TenantViewSet):
    queryset = PaymentTerm.objects.all()
    serializer_class = PaymentTermSerializer
    required_permission = "payments.view"
    write_permission = "payments.manage"
    search_fields = ["name"]
    filterset_fields = ["is_default"]

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        term = self.get_object()
        PaymentTerm.objects.filter(organization=request.organization).update(is_default=False)
        term.is_default = True
        term.save(update_fields=["is_default", "updated_at"])
        return Response(self.get_serializer(term).data)


class PaymentRunViewSet(TenantViewSet):
    queryset = PaymentRun.objects.all()
    serializer_class = PaymentRunSerializer
    required_permission = "payments.view"
    write_permission = "payments.manage"
    search_fields = ["number"]
    filterset_fields = ["status"]

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        run = self.get_object()
        if run.status != PaymentRun.Status.DRAFT:
            raise ValidationError("Only draft payment runs can be executed.")
        run.status = PaymentRun.Status.EXECUTED
        run.executed_at = timezone.now()
        run.save(update_fields=["status", "executed_at", "updated_at"])
        return Response(self.get_serializer(run).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        run = self.get_object()
        if run.status != PaymentRun.Status.DRAFT:
            raise ValidationError("Only draft payment runs can be cancelled.")
        run.status = PaymentRun.Status.CANCELLED
        run.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(run).data)


class PaymentAllocationViewSet(TenantViewSet):
    queryset = PaymentAllocation.objects.select_related("payment")
    serializer_class = PaymentAllocationSerializer
    required_permission = "payments.view"
    write_permission = "payments.manage"
    search_fields = ["invoice_ref", "payment__reference"]
    filterset_fields = ["payment"]
