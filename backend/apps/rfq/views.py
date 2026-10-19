from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.core.services import next_number
from apps.rfq.models import Rfq, RfqLine, RfqResponse, RfqResponseLine
from apps.rfq.serializers import (
    RfqLineSerializer,
    RfqResponseLineSerializer,
    RfqResponseSerializer,
    RfqSerializer,
)


class RfqViewSet(TenantViewSet):
    queryset = Rfq.objects.select_related().prefetch_related("lines", "responses")
    serializer_class = RfqSerializer
    required_permission = "rfq.view"
    write_permission = "rfq.manage"
    search_fields = ["number", "title", "notes"]
    filterset_fields = ["status"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
            number=next_number(Rfq, self.request.organization, "RFQ"),
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        responses = RfqResponse.objects.filter(rfq__organization=request.organization)
        by_status = dict(qs.values_list("status").annotate(count=Count("id")))
        return Response(
            {
                "rfqs": qs.count(),
                "draft": by_status.get("draft", 0),
                "open": by_status.get("open", 0),
                "sent": by_status.get("sent", 0),
                "closed": by_status.get("closed", 0),
                "awarded": by_status.get("awarded", 0),
                "cancelled": by_status.get("cancelled", 0),
                "lines": RfqLine.objects.filter(rfq__organization=request.organization).count(),
                "responses": responses.count(),
                "submitted_responses": responses.filter(status=RfqResponse.Status.SUBMITTED).count(),
                "target_value": RfqLine.objects.filter(rfq__organization=request.organization).aggregate(
                    total=Sum("target_price")
                )["total"]
                or 0,
            }
        )

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        rfq = self.get_object()
        rfq.status = Rfq.Status.SENT
        rfq.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(rfq).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        rfq = self.get_object()
        rfq.status = Rfq.Status.CANCELLED
        rfq.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(rfq).data)

    @action(detail=True, methods=["post"])
    def award(self, request, pk=None):
        rfq = self.get_object()
        response_id = request.data.get("response_id")
        if not response_id:
            RfqResponse.objects.filter(rfq=rfq, organization=request.organization).exclude(id=response_id).update(
                status=RfqResponse.Status.WITHDRAWN
            )
            RfqResponse.objects.filter(rfq=rfq, organization=request.organization, id=response_id).update(
                status=RfqResponse.Status.SUBMITTED
            )
        rfq.status = Rfq.Status.AWARDED
        rfq.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(rfq).data)


class RfqLineViewSet(TenantViewSet):
    queryset = RfqLine.objects.select_related("rfq", "product")
    serializer_class = RfqLineSerializer
    required_permission = "rfq.view"
    write_permission = "rfq.manage"
    filterset_fields = ["rfq", "product"]


class RfqResponseViewSet(TenantViewSet):
    queryset = RfqResponse.objects.select_related("rfq", "supplier").prefetch_related("lines")
    serializer_class = RfqResponseSerializer
    required_permission = "rfq.view"
    write_permission = "rfq.manage"
    search_fields = ["rfq__number", "supplier__name"]
    filterset_fields = ["rfq", "supplier", "status"]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        response = self.get_object()
        response.status = RfqResponse.Status.SUBMITTED
        response.submitted_at = timezone.now()
        response.save(update_fields=["status", "submitted_at", "updated_at"])
        return Response(self.get_serializer(response).data)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        response = self.get_object()
        response.status = RfqResponse.Status.WITHDRAWN
        response.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(response).data)


class RfqResponseLineViewSet(TenantViewSet):
    queryset = RfqResponseLine.objects.select_related("response", "product")
    serializer_class = RfqResponseLineSerializer
    required_permission = "rfq.view"
    write_permission = "rfq.manage"
    filterset_fields = ["response", "product"]
