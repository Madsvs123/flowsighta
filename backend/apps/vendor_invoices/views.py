from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.core.services import next_number
from apps.vendor_invoices.models import (
    InvoiceApproval,
    InvoiceMatch,
    VendorInvoice,
    VendorInvoiceLine,
)
from apps.vendor_invoices.serializers import (
    InvoiceApprovalSerializer,
    InvoiceMatchSerializer,
    VendorInvoiceLineSerializer,
    VendorInvoiceSerializer,
)


class VendorInvoiceViewSet(TenantViewSet):
    queryset = VendorInvoice.objects.select_related("supplier").prefetch_related("lines", "approvals")
    serializer_class = VendorInvoiceSerializer
    required_permission = "vendor_invoices.view"
    write_permission = "vendor_invoices.manage"
    search_fields = ["number", "supplier__name"]
    filterset_fields = ["status", "supplier"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
            number=next_number(VendorInvoice, self.request.organization, "VI"),
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = dict(qs.values_list("status").annotate(count=Count("id")))
        totals = qs.aggregate(total=Sum("total"), subtotal=Sum("subtotal"), tax=Sum("tax_total"))
        unpaid = qs.exclude(status__in=[VendorInvoice.Status.PAID, VendorInvoice.Status.VOID])
        overdue = unpaid.filter(due_date__gt=timezone.localdate())
        return Response(
            {
                "invoices": qs.count(),
                "received": by_status.get("received", 0),
                "in_review": by_status.get("in_review", 0),
                "approved": by_status.get("approved", 0),
                "paid": by_status.get("paid", 0),
                "void": by_status.get("void", 0),
                "subtotal": totals["subtotal"] or 0,
                "tax_total": totals["tax"] or 0,
                "total": totals["total"] or 0,
                "outstanding": unpaid.aggregate(total=Sum("total"))["total"] or 0,
                "overdue": overdue.count(),
                "overdue_amount": overdue.aggregate(total=Sum("total"))["total"] or 0,
            }
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = VendorInvoice.Status.APPROVED
        invoice.save(update_fields=["status", "updated_at"])
        InvoiceApproval.objects.create(
            organization=invoice.organization,
            invoice=invoice,
            approver=request.user,
            status=InvoiceApproval.Status.APPROVED,
            decided_at=timezone.now(),
            created_by=request.user,
            updated_by=request.user,
        )
        return Response(self.get_serializer(invoice).data)

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = VendorInvoice.Status.PAID
        invoice.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(invoice).data)

    @action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = VendorInvoice.Status.VOID
        invoice.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(invoice).data)


class VendorInvoiceLineViewSet(TenantViewSet):
    queryset = VendorInvoiceLine.objects.select_related("invoice")
    serializer_class = VendorInvoiceLineSerializer
    required_permission = "vendor_invoices.view"
    write_permission = "vendor_invoices.manage"
    filterset_fields = ["invoice"]


class InvoiceMatchViewSet(TenantViewSet):
    queryset = InvoiceMatch.objects.select_related("invoice_line", "invoice_line__invoice")
    serializer_class = InvoiceMatchSerializer
    required_permission = "vendor_invoices.view"
    write_permission = "vendor_invoices.manage"
    filterset_fields = ["invoice_line", "reference_type"]


class InvoiceApprovalViewSet(TenantViewSet):
    queryset = InvoiceApproval.objects.select_related("invoice", "approver")
    serializer_class = InvoiceApprovalSerializer
    required_permission = "vendor_invoices.view"
    write_permission = "vendor_invoices.manage"
    filterset_fields = ["invoice", "approver", "status"]
