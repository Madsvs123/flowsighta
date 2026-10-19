from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantSerializer, TenantViewSet
from apps.core.services import next_number
from apps.inventory.models import Batch, InventoryMovement, Product, SerialNumber, StockItem


class ProductSerializer(TenantSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "sku",
            "name",
            "description",
            "category",
            "uom",
            "unit_cost",
            "unit_price",
            "abc_class",
            "is_serialized",
            "is_batch_tracked",
            "shelf_life_days",
            "default_lead_time_days",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class StockItemSerializer(TenantSerializer):
    available = serializers.ReadOnlyField()
    below_reorder = serializers.ReadOnlyField()
    below_safety = serializers.ReadOnlyField()
    sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    location_code = serializers.CharField(source="location.code", read_only=True)

    class Meta:
        model = StockItem
        fields = (
            "id",
            "product",
            "sku",
            "product_name",
            "warehouse",
            "warehouse_name",
            "location",
            "location_code",
            "on_hand",
            "reserved",
            "available",
            "incoming",
            "safety_stock",
            "reorder_point",
            "reorder_quantity",
            "max_stock",
            "below_reorder",
            "below_safety",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class BatchSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = Batch
        fields = (
            "id",
            "product",
            "sku",
            "warehouse",
            "batch_number",
            "quantity",
            "manufactured_on",
            "expires_on",
            "supplier",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SerialNumberSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = SerialNumber
        fields = ("id", "product", "sku", "warehouse", "serial", "status", "batch", "created_at")
        read_only_fields = ("id", "created_at")


class InventoryMovementSerializer(TenantSerializer):
    sku = serializers.CharField(source="product.sku", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = InventoryMovement
        fields = (
            "id",
            "product",
            "sku",
            "warehouse",
            "warehouse_name",
            "from_location",
            "to_location",
            "kind",
            "quantity",
            "reference_type",
            "reference_id",
            "batch_number",
            "serial",
            "reason",
            "occurred_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ProductViewSet(TenantViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    required_permission = "inventory.view"
    write_permission = "inventory.manage"
    search_fields = ["sku", "name", "category"]
    filterset_fields = ["is_active", "category", "abc_class", "is_serialized", "is_batch_tracked"]


class StockItemViewSet(TenantViewSet):
    queryset = StockItem.objects.select_related("product", "warehouse", "location")
    serializer_class = StockItemSerializer
    required_permission = "inventory.view"
    write_permission = "inventory.manage"
    search_fields = ["product__sku", "product__name", "warehouse__code"]
    filterset_fields = ["warehouse", "product", "location"]

    @action(detail=False, methods=["get"])
    def health(self, request)
        qs = self.get_queryset()
        return Response(
            {
                "sku_count": qs.values("product").distinct().count(),
                "below_reorder": sum(1 for s in qs if s.below_reorder),
                "below_safety": sum(1 for s in qs if s.below_safety),
                "on_hand_value": float(sum((s.on_hand or 0) * (s.product.unit_cost or 0) for s in qs.select_related("product"))),
                "incoming_units": float(sum(s.incoming or 0 for s in qs)),
            }
        )

    @action(detail=True, methods=["post"])
    def reserve(self, request, pk=None):
        item = self.get_object()
        qty = Decimal(str(request.data.get("quantity", 0)))
        if qty > item.available:
            return Response({"detail": "Insufficient available stock"}, status=400)
        item.reserved += qty
        item.save(update_fields=["reserved"])
        InventoryMovement.objects.create(
            organization=item.organization,
            product=item.product,
            warehouse=item.warehouse,
            from_location=item.location,
            kind=InventoryMovement.Kind.RESERVE,
            quantity=qty,
            occurred_at=timezone.now(),
            created_by=request.user,
            reason=request.data.get("reason", ""),
        )
        return Response(self.get_serializer(item).data)

    @action(detail=True, methods=["post"])
    def adjust(self, request, pk=None):
        item = self.get_object()
        qty = Decimal(str(request.data.get("quantity", 0)))
        item.on_hand += qty
        item.save(update_fields=["on_hand"])
        InventoryMovement.objects.create(
            organization=item.organization,
            product=item.product,
            warehouse=item.warehouse,
            to_location=item.location,
            kind=InventoryMovement.Kind.ADJUSTMENT,
            quantity=qty,
            occurred_at=timezone.now(),
            created_by=request.user,
            reason=request.data.get("reason", "Manual adjustment"),
        )
        return Response(self.get_serializer(item).data)


class BatchViewSet(TenantViewSet):
    queryset = Batch.objects.select_related("product", "warehouse")
    serializer_class = BatchSerializer
    required_permission = "inventory.view"
    write_permission = "inventory.manage"
    search_fields = ["batch_number", "product__sku"]
    filterset_fields = ["product", "warehouse"]


class SerialNumberViewSet(TenantViewSet):
    queryset = SerialNumber.objects.select_related("product", "warehouse")
    serializer_class = SerialNumberSerializer
    required_permission = "inventory.view"
    write_permission = "inventory.manage"
    search_fields = ["serial", "product__sku"]
    filterset_fields = ["product", "warehouse", "status"]


class InventoryMovementViewSet(TenantViewSet):
    queryset = InventoryMovement.objects.select_related("product", "warehouse")
    serializer_class = InventoryMovementSerializer
    required_permission = "inventory.view"
    write_permission = "inventory.manage"
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["product__sku", "reference_id", "batch_number", "serial"]
    filterset_fields = ["product", "warehouse", "kind"]

    def perform_create(self, serializer):
        movement = serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            occurred_at=serializer.validated_data.get("occurred_at") or timezone.now(),
        )
        stock, _ = StockItem.objects.get_or_create(
            organization=movement.organization,
            product=movement.product,
            warehouse=movement.warehouse,
            location=movement.to_location or movement.from_location,
            defaults={},
        )
        if movement.kind in (InventoryMovement.Kind.RECEIPT, InventoryMovement.Kind.RETURN, InventoryMovement.Kind.ADJUSTMENT):
            stock.on_hand += movement.quantity
        elif movement.kind in (InventoryMovement.Kind.ISSUE, InventoryMovement.Kind.SCRAP):
            stock.on_hand += movement.quantity
        stock.save(update_fields=["on_hand"])
