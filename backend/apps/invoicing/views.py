from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.invoicing.models import CreditNote, CustomerInvoice, InvoiceLine
from apps.invoicing.serializers import (
    CreditNoteSerializer,
    CustomerInvoiceSerializer,
    InvoiceLineSerializer,
)


class CustomerInvoiceViewSet(TenantViewSet):
    queryset = CustomerInvoice.objects.prefetch_related("lines", "credit_notes")
    serializer_class = CustomerInvoiceSerializer
    required_permission = "invoicing.view"
    write_permission = "invoicing.manage"
    search_fields = ["number", "customer_ref"]
    filterset_fields = ["status", "issue_date", "due_date", "currency"]

    @action(detail=False, methods=["get"])
    def summary(self, request)
        qs = self.get_queryset()
        agg = qs.aggregate(subtotal=Sum("subtotal"), tax_total=Sum("tax_total"), total=Sum("total"))
        outstanding = qs.exclude(status__in=[CustomerInvoice.Status.PAID, CustomerInvoice.Status.VOID]).aggregate(
            total=Sum("total")
        )
        return Response(
            {
                "invoices": qs.count(),
                "draft": qs.filter(status=CustomerInvoice.Status.DRAFT).count(),
                "sent": qs.filter(status=CustomerInvoice.Status.SENT).count(),
                "paid": qs.filter(status=CustomerInvoice.Status.PAID).count(),
                "overdue": qs.filter(status=CustomerInvoice.Status.OVERDUE).count(),
                "subtotal": float(agg["subtotal"] or 0),
                "tax_total": float(agg["tax_total"] or 0),
                "total": float(agg["total"] or 0),
                "outstanding": float(outstanding["total"] or 0),
                "credit_notes": float(
                    CreditNote.objects.filter(organization=request.organization).aggregate(total=Sum("amount"))[
                        "total"
                    ]
                    or 0
                ),
            }
        )

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        invoice = self.get_object()
        if invoice.status == CustomerInvoice.Status.DRAFT:
            raise ValidationError("Only draft invoices can be sent.")
        invoice.status = CustomerInvoice.Status.SENT
        invoice.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(invoice).data)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        if invoice.status not in (CustomerInvoice.Status.SENT, CustomerInvoice.Status.PARTIAL, CustomerInvoice.Status.OVERDUE):
            raise ValidationError("Only issued invoices can be marked paid.")
        invoice.status = CustomerInvoice.Status.PAID
        invoice.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(invoice).data)

    @action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        invoice = self.get_object()
        if invoice.status == CustomerInvoice.Status.PAID:
            raise ValidationError("Paid invoices cannot be voided.")
        invoice.status = CustomerInvoice.Status.VOID
        invoice.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(invoice).data)


class InvoiceLineViewSet(TenantViewSet):
    queryset = InvoiceLine.objects.select_related("invoice")
    serializer_class = InvoiceLineSerializer
    required_permission = "invoicing.view"
    write_permission = "invoicing.manage"
    search_fields = ["description", "invoice__number"]
    filterset_fields = ["invoice"]


class CreditNoteViewSet(TenantViewSet):
    queryset = CreditNote.objects.select_related("invoice")
    serializer_class = CreditNoteSerializer
    required_permission = "invoicing.view"
    write_permission = "invoicing.manage"
    search_fields = ["number", "reason", "invoice__number"]
    filterset_fields = ["invoice", "status"]

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        note = self.get_object()
        if note.status != CreditNote.Status.DRAFT:
            raise ValidationError("Only draft credit notes can be issued.")
        note.status = CreditNote.Status.ISSUED
        note.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(note).data)

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        note = self.get_object()
        if note.status != CreditNote.Status.ISSUED:
            raise ValidationError("Only issued credit notes can be applied.")
        note.status = CreditNote.Status.APPLIED
        note.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(note).data)
