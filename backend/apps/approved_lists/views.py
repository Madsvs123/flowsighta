from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.approved_lists.models import ApprovedList, ApprovedSupplier
from apps.approved_lists.serializers import ApprovedListSerializer, ApprovedSupplierSerializer
from apps.core.mixins import TenantViewSet


class ApprovedListViewSet(TenantViewSet):
    queryset = ApprovedList.objects.all()
    serializer_class = ApprovedListSerializer
    required_permission = "approved_lists.view"
    write_permission = "approved_lists.manage"
    search_fields = ["name", "category", "description"]
    filterset_fields = ["status", "category"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        entries = ApprovedSupplier.objects.filter(organization=request.organization)
        return Response(
            {
                "list_count": qs.count(),
                "active_lists": qs.filter(status=ApprovedList.Status.ACTIVE).count(),
                "supplier_entries": entries.count(),
                "approved_suppliers": entries.filter(status=ApprovedSupplier.Status.APPROVED).count(),
                "pending_suppliers": entries.filter(status=ApprovedSupplier.Status.PENDING).count(),
                "on_hold_suppliers": entries.filter(status=ApprovedSupplier.Status.ON_HOLD).count(),
                "revoked_suppliers": entries.filter(status=ApprovedSupplier.Status.REVOKED).count(),
                "average_rating": float(
                    entries.filter(rating__gt=0).aggregate(v=Avg("rating"))["v"] or 0
                ),
                "suppliers_per_list": list(
                    qs.annotate(entry_count=Count("approved_suppliers"))
                    .order_by("-entry_count")[:5]
                    .values("name", "entry_count", "status")
                ),
            }
        )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        list_obj = self.get_object()
        list_obj.status = ApprovedList.Status.INACTIVE
        list_obj.save(update_fields=["status", "updated_at"])
        list_obj.approved_suppliers.filter(status=ApprovedSupplier.Status.APPROVED).update(
            status=ApprovedSupplier.Status.ON_HOLD, updated_at=timezone.now()
        )
        return Response(self.get_serializer(list_obj).data)


class ApprovedSupplierViewSet(TenantViewSet):
    queryset = ApprovedSupplier.objects.select_related("list", "supplier")
    serializer_class = ApprovedSupplierSerializer
    required_permission = "approved_lists.view"
    write_permission = "approved_lists.manage"
    search_fields = ["supplier__name", "supplier__code", "list__name", "notes"]
    filterset_fields = ["list", "supplier", "status"]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        entry = self.get_object()
        entry.status = ApprovedSupplier.Status.ON_HOLD
        entry.approved_at = timezone.now()
        rating = request.data.get("rating")
        if rating is not None:
            entry.rating = rating
        entry.save(update_fields=["status", "approved_at", "rating", "updated_at"])
        return Response(self.get_serializer(entry).data)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        entry = self.get_object()
        entry.status = ApprovedSupplier.Status.REVOKED
        entry.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(entry).data)
