from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.collaboration.models import Activity, Notification, SearchIndex, Task
from apps.core.services import upsert_search
from apps.events.models import SupplyChainEvent
from apps.inventory.models import Batch, InventoryMovement, Product, SerialNumber, StockItem
from apps.logistics.models import (
    Carrier,
    CarrierServiceLevel,
    Container,
    FreightCost,
    LogisticsException,
    Package,
    Route,
    Shipment,
    ShipmentMilestone,
    TrackingEvent,
)
from apps.organizations.models import Customer, Location, Membership, Organization, Region, Team, Warehouse
from apps.organizations.services import provision_organization
from apps.planning.models import HistoricalDemand, PlanningConfig
from apps.planning.views import recompute_plan
from apps.procurement.models import PurchaseOrder, PurchaseOrderLine, Requisition, RequisitionLine
from apps.procurement.services import issue_purchase_order, record_po_status
from apps.suppliers.models import (
    OnboardingStep,
    PurchaseHistory,
    Supplier,
    SupplierCertification,
    SupplierContact,
    SupplierContract,
    SupplierProduct,
)


class Command(BaseCommand):
    help = "Seed a complete FlowSighta demo organization with operational data."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            email="ava.chen@northline.example",
            defaults={
                "first_name": "Ava",
                "last_name": "Chen",
                "job_title": "VP Supply Chain",
                "is_active": True,
            },
        )
        if created:
            user.set_password("FlowSighta!23")
            user.save()
        org = Organization.objects.filter(slug="northline-industrial").first()
        if org is None:
            org = provision_organization("Northline Industrial", "manufacturer", user)
            org.slug = "northline-industrial"
            org.industry = "Industrial equipment"
            org.currency = "USD"
            org.save(update_fields=["slug", "industry", "currency"])
        else:
            Membership.objects.get_or_create(
                organization=org,
                user=user,
                defaults={"role": org.organizations_role_set.filter(name="Owner").first()},
            )

        role_owner = org.role_set.filter(name="Owner").first()
        Membership.objects.update_or_create(organization=org, user=user, defaults={"role": role_owner, "is_default": False, "is_active": True})

        amer, _ = Region.objects.get_or_create(organization=org, code="AMER", defaults={"name": "Americas", "country": "US", "timezone": "America/Chicago"})
        emea, _ = Region.objects.get_or_create(organization=org, code="EMEA", defaults={"name": "Europe", "country": "DE", "timezone": "Europe/Berlin"})
        Team.objects.get_or_create(organization=org, name="Procurement", defaults={"region": amer})
        Team.objects.get_or_create(organization=org, name="Logistics Control Tower", defaults={"region": amer})

        chi, _ = Warehouse.objects.get_or_create(
            organization=org,
            code="CHI-DC",
            defaults={
                "name": "Chicago Distribution Center",
                "kind": Warehouse.Kind.DISTRIBUTION_CENTER,
                "region": amer,
                "city": "Chicago",
                "state": "IL",
                "country": "US",
                "capacity_units": 48000,
                "used_capacity_units": 31200,
                "manager_email": "chi-dc@northline.example",
            },
        )
        rot, _ = Warehouse.objects.get_or_create(
            organization=org,
            code="RTM-WH",
            defaults={
                "name": "Rotterdam Warehouse",
                "kind": Warehouse.Kind.WAREHOUSE,
                "region": emea,
                "city": "Rotterdam",
                "country": "NL",
                "capacity_units": 26000,
                "used_capacity_units": 18100,
            },
        )
        dal, _ = Warehouse.objects.get_or_create(
            organization=org,
            code="DAL-PL",
            defaults={
                "name": "Dallas Plant",
                "kind": Warehouse.Kind.PLANT,
                "region": amer,
                "city": "Dallas",
                "state": "TX",
                "country": "US",
                "capacity_units": 20000,
                "used_capacity_units": 16400,
            },
        )
        for wh, zones in ((chi, ["A", "B", "C"]), (rot, ["EU1"]), (dal, ["RAW", "FG"])):
            for z in zones:
                Location.objects.get_or_create(organization=org, warehouse=wh, code=f"{z}-01", defaults={"zone": z, "aisle": "01", "bin": "01"})

        Customer.objects.get_or_create(organization=org, code="CUST-ACME", defaults={"name": "Acme Manufacturing", "segment": "OEM", "country": "US", "city": "Detroit"})
        Customer.objects.get_or_create(organization=org, code="CUST-HELIX", defaults={"name": "Helix Retail Group", "segment": "Retail", "country": "US", "city": "Atlanta"})

        suppliers_data = [
            ("SUP-1001", "Pacific Precision Metals", "China", "low", 91, "metals", 18),
            ("SUP-1044", "Nordic Bearings AB", "Sweden", "medium", 84, "components", 21),
            ("SUP-1108", "Gulfstream Polymers", "USA", "low", 88, "resins", 10),
            ("SUP-1182", "Sahara Castings", "UAE", "high", 61, "castings", 28),
            ("SUP-1210", "Andes Electronics", "Chile", "medium", 76, "electronics", 24),
        ]
        suppliers = {}
        for code, name, country, risk, score, category, lt in suppliers_data:
            s, _ = Supplier.objects.get_or_create(
                organization=org,
                code=code,
                defaults={
                    "name": name,
                    "status": Supplier.Status.ACTIVE,
                    "risk_level": risk,
                    "country": country,
                    "category": category,
                    "performance_score": score,
                    "on_time_delivery_rate": score + 4,
                    "quality_score": score - 2,
                    "fill_rate": score - 6,
                    "total_spend": score * 180,
                    "default_lead_time_days": lt,
                    "preferred": score > 85,
                },
            )
            suppliers[code] = s
            SupplierContact.objects.get_or_create(organization=org, supplier=s, email=f"sales@{code.lower()}.example", defaults={"name": "Sales Desk", "is_primary": True, "role": "Account"})
            SupplierContract.objects.get_or_create(
                organization=org,
                number=f"CTR-{code[-4:]}",
                defaults={"supplier": s, "title": f"Master supply agreement {name}", "status": "active", "value": score * 25000, "payment_terms": "Net 45", "incoterms": "FOB"},
            )
            SupplierCertification.objects.get_or_create(organization=org, supplier=s, name="ISO 9001", defaults={"issuer": "ISO", "status": "valid"})
            if not s.onboarding_steps.exists():
                OnboardingStep.objects.create(organization=org, supplier=s, sequence=1, name="Profile complete", status="complete", completed_at=timezone.now())

        products = [
            ("BRG-6205", "Precision bearing 6205", "components", 18.4, 12, True),
            ("HSG-440", "Cast housing 440mm", "castings", 126.0, 24, False),
            ("PCB-88A", "Controller board 88A", "electronics", 54.2, 20, True),
            ("RES-PP-20", "Polypropylene resin 20kg", "resins", 31.5, 8, False),
            ("STL-PL-12", "Steel plate 12mm", "metals", 89.0, 16, False),
            ("MTR-2KW", "2kW drive motor", "components", 410.0, 30, True),
        ]
        product_map = {}
        loc_chi = chi.locations.first()
        for sku, name, cat, cost, lead, serialized in products:
            p, _ = Product.objects.get_or_create(
                organization=org,
                sku=sku,
                defaults={
                    "name": name,
                    "category": cat,
                    "unit_cost": cost,
                    "unit_price": Decimal(str(cost)) * Decimal("0.35"),
                    "is_serialized": serialized,
                    "is_batch_tracked": not serialized,
                    "default_lead_time_days": lead,
                    "abc_class": "A" if cost > 80 else "B",
                },
            )
            product_map[sku] = p
            for wh, on_hand, reorder, safety in (
                (chi, 420 if cost < 100 else 80, 180, 90),
                (rot, 140, 80, 40),
                (dal, 60 if "MTR" in sku else 210, 70, 35),
            ):
                StockItem.objects.get_or_create(
                    organization=org,
                    product=p,
                    warehouse=wh,
                    location=wh.locations.first(),
                    defaults={
                        "on_hand": on_hand,
                        "reserved": 12,
                        "incoming": 40,
                        "safety_stock": safety,
                        "reorder_point": reorder,
                        "reorder_quantity": reorder * 2,
                    },
                )
            HistoricalDemand.objects.get_or_create(
                organization=org,
                product=p,
                warehouse=chi,
                period_start=timezone.now().date() - timedelta(days=28),
                defaults={"period_end": timezone.now().date() - timedelta(days=21), "quantity": 90 + int(cost)},
            )
            upsert_search(org, p, p.name, p.sku, p.category, f"/inventory/{p.id}")

        SupplierProduct.objects.get_or_create(
            organization=org,
            supplier=suppliers["SUP-1044"],
            sku="BRG-6205",
            defaults={"name": "Precision bearing 6205", "unit_price": 17.9, "lead_time_days": 21, "moq": 100, "catalog_product_id": product_map["BRG-6205"].id},
        )
        SupplierProduct.objects.get_or_create(
            organization=org,
            supplier=suppliers["SUP-1182"],
            sku="HSG-440",
            defaults={"name": "Cast housing 440mm", "unit_price": 119, "lead_time_days": 28, "moq": 10, "catalog_product_id": product_map["HSG-440"].id},
        )

        Batch.objects.get_or_create(organization=org, product=product_map["RES-PP-20"], batch_number="B-24081", defaults={"warehouse": chi, "quantity": 200, "expires_on": timezone.now().date() + timedelta(days=240)})
        SerialNumber.objects.get_or_create(organization=org, serial="MTR-2KW-000441", defaults={"product": product_map["MTR-2KW"], "warehouse": dal, "status": "in_stock"})
        InventoryMovement.objects.get_or_create(
            organization=org,
            product=product_map["BRG-6205"],
            warehouse=chi,
            kind="receipt",
            quantity=200,
            occurred_at=timezone.now() - timedelta(days=3),
            defaults={"reason": "PO receipt", "reference_type": "GoodsReceipt", "reference_id": "seed"},
        )

        req, _ = Requisition.objects.get_or_create(
            organization=org,
            number="REQ-2026-00012",
            defaults={"title": "Q3 bearing replenishment", "status": "approved", "requester": user, "warehouse": chi, "needed_by": timezone.now().date() + timedelta(days=180), "total_amount": 17900, "created_by": user},
        )
        RequisitionLine.objects.get_or_create(organization=org, requisition=req, sku="BRG-6205", defaults={"description": "Precision bearing 6205", "quantity": 1000, "estimated_unit_price": 17.9, "suggested_supplier": suppliers["SUP-1044"]})

        po, _ = PurchaseOrder.objects.get_or_create(
            organization=org,
            number="PO-2026-00088",
            defaults={
                "supplier": suppliers["SUP-1044"],
                "warehouse": chi,
                "status": "issued",
                "expected_delivery_date": timezone.now().date() + timedelta(days=12),
                "subtotal": 17900,
                "total_amount": 18640,
                "issued_at": timezone.now() - timedelta(days=6),
                "created_by": user,
            },
        )
        PurchaseOrderLine.objects.get_or_create(
            organization=org,
            purchase_order=po,
            sku="BRG-6205",
            defaults={"description": "Precision bearing 6205", "quantity_ordered": 1000, "unit_price": 17.9, "product": product_map["BRG-6205"], "warehouse": chi, "expected_delivery_date": po.expected_delivery_date},
        )
        PurchaseHistory.objects.get_or_create(organization=org, supplier=suppliers["SUP-1044"], purchase_order_number="PO-2025-00410", defaults={"ordered_on": timezone.now().date() - timedelta(days=80), "received_on": timezone.now().date() - timedelta(days=58), "amount": 15200, "on_time": True})

        ocean, _ = Carrier.objects.get_or_create(organization=org, code="MSC", defaults={"name": "Mediterranean Shipping", "mode": "ocean", "on_time_rate": 86, "performance_score": 84, "scac": "MSCU"})
        truck, _ = Carrier.objects.get_or_create(organization=org, code="XPO", defaults={"name": "XPO Logistics", "mode": "truck", "on_time_rate": 93, "performance_score": 91, "scac": "XPOL"})
        air, _ = Carrier.objects.get_or_create(organization=org, code="LH-CARGO", defaults={"name": "Lufthansa Cargo", "mode": "air", "on_time_rate": 90, "performance_score": 88})
        CarrierServiceLevel.objects.get_or_create(organization=org, carrier=ocean, code="FCL", defaults={"name": "Full container load", "transit_days": 28, "cost_per_kg": 0.18})
        CarrierServiceLevel.objects.get_or_create(organization=org, carrier=truck, code="LTL", defaults={"name": "Less than truckload", "transit_days": 4, "cost_per_kg": 0.62})
        route, _ = Route.objects.get_or_create(organization=org, code="SHA-CHI", defaults={"name": "Shanghai to Chicago", "origin_city": "Shanghai", "origin_country": "CN", "destination_city": "Chicago", "destination_country": "US", "mode": "ocean", "standard_transit_days": 29, "distance_km": 11400})

        shp, _ = Shipment.objects.get_or_create(
            organization=org,
            number="SHP-2026-00451",
            defaults={
                "carrier": ocean,
                "route": route,
                "supplier": suppliers["SUP-1001"],
                "purchase_order": po,
                "status": "in_transit",
                "tracking_number": "MSCU4491208",
                "origin_address": "Shanghai Yangshan",
                "destination_warehouse": chi,
                "destination_address": "Chicago DC",
                "eta": timezone.now() + timedelta(days=9),
                "etd": timezone.now() - timedelta(days=18),
                "atd": timezone.now() - timedelta(days=17),
                "freight_cost": 14820,
                "weight_kg": 18400,
                "current_location": "Pacific Ocean — transpacific lane",
                "customs_status": "pending",
                "created_by": user,
            },
        )
        Container.objects.get_or_create(organization=org, shipment=shp, container_number="MSCU7782134", defaults={"container_type": "40HC", "weight_kg": 18400})
        Package.objects.get_or_create(organization=org, shipment=shp, tracking_number="PKG-451-01", defaults={"sku": "STL-PL-12", "quantity": 40, "weight_kg": 2200})
        TrackingEvent.objects.get_or_create(
            organization=org,
            shipment=shp,
            status="in_transit",
            occurred_at=timezone.now() - timedelta(hours=6),
            defaults={"location": "30.2N 165.4W", "description": "Vessel on schedule", "source": "carrier"},
        )
        if not shp.milestones.exists():
            ShipmentMilestone.objects.create(organization=org, shipment=shp, code="departed", name="Departed origin", sequence=1, planned_at=shp.etd, actual_at=shp.atd)
            ShipmentMilestone.objects.create(organization=org, shipment=shp, code="arrived", name="Arrived destination", sequence=2, planned_at=shp.eta)

        delayed, _ = Shipment.objects.get_or_create(
            organization=org,
            number="SHP-2026-00302",
            defaults={
                "carrier": truck,
                "status": "delayed",
                "supplier": suppliers["SUP-1182"],
                "destination_warehouse": dal,
                "eta": timezone.now() - timedelta(days=1),
                "delay_minutes": 1560,
                "freight_cost": 2100,
                "current_location": "Oklahoma City, OK",
                "tracking_number": "XPO991244",
                "created_by": user,
            },
        )
        LogisticsException.objects.get_or_create(organization=org, shipment=delayed, code="WEATHER", defaults={"severity": "high", "description": "Severe weather hold on I-35 corridor", "status": "open"})
        FreightCost.objects.get_or_create(organization=org, shipment=shp, charge_type="ocean_freight", defaults={"amount": 13200, "currency": "USD"})

        SupplyChainEvent.objects.get_or_create(
            organization=org,
            number="EVT-2026-00019",
            defaults={
                "title": "Delayed inbound housing castings",
                "category": "delayed_shipment",
                "severity": "high",
                "status": "open",
                "shipment": delayed,
                "supplier": suppliers["SUP-1182"],
                "detected_at": timezone.now() - timedelta(hours=8),
                "description": "Dallas plant will miss tomorrow's production slot if the XPO trailer does not clear weather hold.",
                "impact_score": 78,
            },
        )
        SupplyChainEvent.objects.get_or_create(
            organization=org,
            number="EVT-2026-00021",
            defaults={
                "title": "Safety stock risk on 2kW motors",
                "category": "inventory_risk",
                "severity": "medium",
                "status": "acknowledged",
                "warehouse": dal,
                "product_sku": "MTR-2KW",
                "detected_at": timezone.now() - timedelta(days=1),
                "description": "Available stock is approaching safety cover at Dallas plant.",
            },
        )

        PlanningConfig.objects.get_or_create(organization=org, defaults={"horizon_weeks": 12, "service_level_target": 96})
        recompute_plan(org)

        Task.objects.get_or_create(organization=org, title="Expedite Sahara Castings trailer", defaults={"priority": "high", "assignee": user, "related_type": "Shipment", "related_id": str(delayed.id), "due_date": timezone.now().date()})
        Notification.objects.get_or_create(organization=org, user=user, title="Delayed inbound housing castings", defaults={"body": "XPO trailer still in weather hold.", "category": "alert", "severity": "high", "link": "/alerts"})
        Activity.objects.get_or_create(organization=org, verb="seeded", object_type="Organization", defaults={"actor": user, "summary": "Demo dataset loaded for Northline Industrial", "object_id": str(org.id)})
        upsert_search(org, org, org.name, "Manufacturer", "northline industrial demo", "/settings")
        upsert_search(org, shp, shp.number, shp.tracking_number, "ocean chicago", f"/shipments/{shp.id}")
        upsert_search(org, suppliers["SUP-1044"], "Nordic Bearings AB", "SUP-1044", "bearings sweden", f"/suppliers/{suppliers['SUP-1044'].id}")

        self.stdout.write(self.style.SUCCESS("Seeded Northline Industrial. Login: ava.chen@northline.example / FlowSighta!23"))
