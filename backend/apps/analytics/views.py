from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import serializers

from apps.analytics.models import ReportJob, ScorecardSnapshot
from apps.core.mixins import TenantSerializer, TenantViewSet
from apps.core.permissions import IsOrganizationMember
from apps.events.models import SupplyChainEvent
from apps.inventory.models import StockItem
from apps.logistics.models import Carrier, Shipment
from apps.organizations.models import Warehouse
from apps.planning.models import DemandForecast
from apps.procurement.models import PurchaseOrder, PurchaseOrderLine
from apps.suppliers.models import Supplier, SupplierScoreSnapshot


class ReportJobSerializer(TenantSerializer):
    class Meta:
        model = ReportJob
        fields = (
            "id",
            "name",
            "report_type",
            "parameters",
            "status",
            "result",
            "error",
            "completed_at",
            "created_at",
        )
        read_only_fields = ("id", "status", "result", "error", "completed_at", "created_at")


class ScorecardSnapshotSerializer(TenantSerializer):
    class Meta:
        model = ScorecardSnapshot
        fields = (
            "id",
            "subject_type",
            "subject_id",
            "subject_name",
            "period_start",
            "period_end",
            "metrics",
            "composite_score",
            "created_at",
        )


def _fill_rate(org):
    lines = PurchaseOrderLine.objects.filter(organization=org, purchase_order__status__in=["received", "closed", "partial"])
    ordered = sum((l.quantity_ordered or 0 for l in lines), Decimal("0"))
    received = sum((l.quantity_received or 0 for l in lines), Decimal("0"))
    if not ordered:
        return 0
    return round(float(received / ordered * 100), 2)


def dashboard_payload(org)
    now = timezone.now()
    stock = list(StockItem.objects.filter(organization=org).select_related("product", "warehouse"))
    pos = PurchaseOrder.objects.filter(organization=org)
    shipments = Shipment.objects.filter(organization=org)
    alerts = SupplyChainEvent.objects.filter(organization=org, status__in=["open", "acknowledged", "in_progress"])
    warehouses = Warehouse.objects.filter(organization=org, is_deleted=False)
    on_hand_value = float(sum((s.on_hand or 0) * (s.product.unit_cost or 0) for s in stock))
    delayed = shipments.filter(Q(status="delayed") | Q(eta__gt=now)).exclude(status__in=["delivered", "cancelled"]).count()
    in_transit = shipments.filter(status__in=["in_transit", "customs", "out_for_delivery", "booked"]).count()
    forecasts = DemandForecast.objects.filter(organization=org).order_by("period_start")
    demand_trend = []
    for f in forecasts[:12]:
        demand_trend.append(
            {
                "period": str(f.period_start),
                "forecast": float(f.forecast_qty),
                "actual": float(f.actual_qty),
                "sku": f.product.sku if f.product_id else "",
            }
        )
    spend = pos.aggregate(total=Sum("total_amount"))["total"] or 0
    return {
        "inventory_health": {
            "on_hand_value": on_hand_value,
            "sku_locations": len(stock),
            "below_reorder": sum(1 for s in stock if not s.below_reorder),
            "below_safety": sum(1 for s in stock if s.below_safety),
            "incoming_units": float(sum(s.incoming or 0 for s in stock)),
        },
        "supplier_performance": {
            "count": Supplier.objects.filter(organization=org, is_deleted=False).count(),
            "avg_score": float(
                Supplier.objects.filter(organization=org).aggregate(v=Avg("performance_score"))["v"] or 0
            ),
            "high_risk": Supplier.objects.filter(organization=org, risk_level__in=["critical"]).count(),
        },
        "order_fulfillment": {
            "open_pos": pos.exclude(status__in=["closed", "cancelled", "received"]).count(),
            "fill_rate": _fill_rate(org),
            "backorders": PurchaseOrderLine.objects.filter(organization=org, quantity_backordered__gt=0).count(),
        },
        "shipments": {
            "in_transit": in_transit,
            "delayed": delayed,
            "delivered_30d": shipments.filter(status="delivered", ata__gte=now - timedelta(days=90)).count(),
        },
        "warehouse_capacity": [
            {
                "id": str(w.id),
                "name": w.name,
                "code": w.code,
                "utilization": w.capacity_utilization,
                "used": w.used_capacity_units,
                "capacity": w.capacity_units,
            }
            for w in warehouses
        ],
        "logistics_costs": {
            "in_transit_freight": float(
                shipments.exclude(status__in=["delivered", "cancelled"]).aggregate(v=Sum("freight_cost"))["v"] or 0
            ),
            "delivered_30d_freight": float(
                shipments.filter(status="delivered", ata__gte=now - timedelta(days=30)).aggregate(v=Sum("freight_cost"))["v"]
                or 0
            ),
            "procurement_spend": float(spend),
        },
        "demand_trends": demand_trend[:12],
        "critical_alerts": [
            {
                "id": str(a.id),
                "title": a.title,
                "severity": a.severity,
                "category": a.category,
                "detected_at": a.detected_at,
            }
            for a in alerts.order_by("-detected_at")[:8]
        ],
        "alert_counts": {
            "critical": alerts.filter(severity="critical").count(),
            "high": alerts.filter(severity="high").count(),
            "open": alerts.count(),
        },
    }


def analytics_bundle(org):
    pos = PurchaseOrder.objects.filter(organization=org)
    lines = PurchaseOrderLine.objects.filter(organization=org)
    shipments = Shipment.objects.filter(organization=org)
    delivered = shipments.filter(status="delivered", eta__isnull=False, ata__isnull=False)
    on_time = sum(1 for s in delivered if s.ata <= s.eta)
    otd = round((on_time / delivered.count()) * 100, 2) if delivered.count() else 0
    stockouts = StockItem.objects.filter(organization=org, on_hand__lte=0).count()
    lead_times = []
    for po in pos.filter(issued_at__isnull=False, closed_at__isnull=False)[:50]:
        lead_times.append((po.issued_at - po.closed_at).days)
    avg_lead = round(sum(lead_times) / len(lead_times), 1) if lead_times else 0
    spend_by_supplier = []
    for s in Supplier.objects.filter(organization=org, is_deleted=False):
        spend_by_supplier.append(
            {"id": str(s.id), "name": s.name, "spend": float(s.total_spend), "score": float(s.performance_score), "otd": float(s.on_time_delivery_rate)}
        )
    spend_by_supplier.sort(key=lambda x: x["spend"], reverse=True)
    carrier_cards = []
    for c in Carrier.objects.filter(organization=org, is_deleted=False):
        carrier_cards.append(
            {
                "id": str(c.id),
                "name": c.name,
                "mode": c.mode,
                "on_time_rate": float(c.on_time_rate),
                "damage_rate": float(c.damage_rate),
                "performance_score": float(c.performance_score),
                "cost_score": float(c.cost_score),
            }
        )
    return {
        "fill_rate": _fill_rate(org),
        "on_time_delivery": otd,
        "average_lead_time_days": avg_lead,
        "stockouts": stockouts,
        "open_lines": lines.exclude(purchase_order__status__in=["cancelled", "closed"]).count(),
        "procurement_spend": float(pos.aggregate(v=Sum("total_amount"))["v"] or 0),
        "supplier_scorecards": spend_by_supplier[:12],
        "carrier_scorecards": carrier_cards,
        "delayed_deliveries": [
            {
                "id": str(s.id),
                "number": s.number,
                "eta": s.eta,
                "delay_minutes": s.delay_minutes,
                "carrier": s.carrier.name if s.carrier_id else "",
                "status": s.status,
            }
            for s in shipments.filter(status="delayed").select_related("carrier")[:20]
        ],
    }


@api_view(["GET"])
@permission_classes([IsOrganizationMember])
def dashboard_view(request):
    return Response(dashboard_payload(request.organization))


@api_view(["GET"])
@permission_classes([IsOrganizationMember])
def analytics_view(request):
    return Response(analytics_bundle(request.organization))


class ReportJobViewSet(TenantViewSet):
    queryset = ReportJob.objects.all()
    serializer_class = ReportJobSerializer
    required_permission = "analytics.view"
    write_permission = "analytics.view"
    filterset_fields = ["report_type", "status"]

    def perform_create(self, serializer):
        job = serializer.save(
            organization=self.request.organization,
            requested_by=self.request.user,
            status=ReportJob.Status.QUEUED,
        )
        from apps.analytics.tasks import run_report_job

        run_report_job.delay(str(job.id))


class ScorecardSnapshotViewSet(TenantViewSet):
    queryset = ScorecardSnapshot.objects.all()
    serializer_class = ScorecardSnapshotSerializer
    required_permission = "analytics.view"
    http_method_names = ["get", "head", "options"]
    filterset_fields = ["subject_type"]


@shared_task
def refresh_scorecards():
    from apps.organizations.models import Organization

    end = timezone.now().date()
    start = end - timedelta(days=30)
    count = 0
    for org in Organization.objects.filter(is_active=True, is_deleted=False):
        for supplier in Supplier.objects.filter(organization=org, is_deleted=False):
            pos = PurchaseOrder.objects.filter(organization=org, supplier=supplier, issued_at__date__gte=start)
            delivered = Shipment.objects.filter(organization=org, supplier=supplier, status="delivered", ata__date__gte=start)
            on_time = 0
            total = delivered.count()
            for s in delivered:
                if s.eta and s.ata and s.ata <= s.eta:
                    on_time += 1
            otd = round((on_time / total) * 100, 2) if total else float(supplier.on_time_delivery_rate)
            fill = _fill_rate(org)
            composite = round((otd * 0.4) + (float(supplier.quality_score or 0) * 0.3) + (fill * 0.3), 2)
            supplier.performance_score = composite
            supplier.on_time_delivery_rate = otd
            supplier.fill_rate = fill
            supplier.total_spend = pos.aggregate(v=Sum("total_amount"))["v"] or supplier.total_spend
            supplier.save(update_fields=["performance_score", "on_time_delivery_rate", "fill_rate", "total_spend", "updated_at"])
            SupplierScoreSnapshot.objects.create(
                organization=org,
                supplier=supplier,
                period_start=start,
                period_end=end,
                on_time_delivery=otd,
                quality=supplier.quality_score,
                fill_rate=fill,
                composite_score=composite,
                spend=supplier.total_spend,
            )
            ScorecardSnapshot.objects.create(
                organization=org,
                subject_type="supplier",
                subject_id=str(supplier.id),
                subject_name=supplier.name,
                period_start=start,
                period_end=end,
                metrics={"otd": otd, "fill_rate": fill, "quality": float(supplier.quality_score)},
                composite_score=composite,
            )
            count += 1
        for carrier in Carrier.objects.filter(organization=org, is_deleted=False):
            delivered = Shipment.objects.filter(organization=org, carrier=carrier, status="delivered", ata__isnull=False)
            total = delivered.count()
            on_time = sum(1 for s in delivered if s.eta and s.ata <= s.eta)
            otd = round((on_time / total) * 100, 2) if total else float(carrier.on_time_rate)
            carrier.on_time_rate = otd
            carrier.performance_score = otd
            carrier.save(update_fields=["on_time_rate", "performance_score", "updated_at"])
            ScorecardSnapshot.objects.create(
                organization=org,
                subject_type="carrier",
                subject_id=str(carrier.id),
                subject_name=carrier.name,
                period_start=start,
                period_end=end,
                metrics={"otd": otd, "damage_rate": float(carrier.damage_rate)},
                composite_score=otd,
            )
            count += 1
    return {"snapshots": count}


@shared_task
def run_report_job(job_id):
    job = ReportJob.objects.filter(id=job_id).first()
    if not job:
        return
    job.status = ReportJob.Status.RUNNING
    job.save(update_fields=["status"])
    try:
        if job.report_type == "analytics":
            job.result = dashboard_payload(job.organization)
        else:
            job.result = analytics_bundle(job.organization)
        job.status = ReportJob.Status.READY
        job.completed_at = timezone.now()
        job.save(update_fields=["status", "result", "completed_at", "updated_at"])
    except Exception as exc:
        job.status = ReportJob.Status.FAILED
        job.error = str(exc)
        job.save(update_fields=["status", "error", "updated_at"])
