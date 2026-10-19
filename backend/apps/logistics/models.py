from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class Carrier(TenantModel, AuditedModel, SoftDeleteModel):
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=160)
    scac = models.CharField(max_length=10, blank=True)
    mode = models.CharField(max_length=40, default="truck")
    country = models.CharField(max_length=80, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    tracking_url_template = models.CharField(max_length=240, blank=True)
    on_time_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    damage_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cost_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "code")
        ordering = ["name"]


class CarrierServiceLevel(TenantModel):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, related_name="service_levels")
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=120)
    transit_days = models.PositiveIntegerField(default=3)
    cost_per_kg = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("carrier", "code")


class Route(TenantModel, AuditedModel):
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=160)
    origin_country = models.CharField(max_length=80, blank=True)
    origin_city = models.CharField(max_length=120, blank=True)
    destination_country = models.CharField(max_length=80, blank=True)
    destination_city = models.CharField(max_length=120, blank=True)
    mode = models.CharField(max_length=40, default="truck")
    standard_transit_days = models.PositiveIntegerField(default=5)
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "code")


class Shipment(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        BOOKED = "booked", "Booked"
        IN_TRANSIT = "in_transit", "In Transit"
        CUSTOMS = "customs", "Customs"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        DELAYED = "delayed", "Delayed"
        EXCEPTION = "exception", "Exception"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=40)
    reference = models.CharField(max_length=80, blank=True)
    purchase_order = models.ForeignKey(
        "procurement.PurchaseOrder", null=True, blank=True, on_delete=models.SET_NULL, related_name="shipments"
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier", null=True, blank=True, on_delete=models.SET_NULL, related_name="shipments"
    )
    customer = models.ForeignKey(
        "organizations.Customer", null=True, blank=True, on_delete=models.SET_NULL, related_name="shipments"
    )
    carrier = models.ForeignKey(Carrier, on_delete=models.PROTECT, related_name="shipments")
    service_level = models.ForeignKey(
        CarrierServiceLevel, null=True, blank=True, on_delete=models.SET_NULL, related_name="shipments"
    )
    route = models.ForeignKey(Route, null=True, blank=True, on_delete=models.SET_NULL, related_name="shipments")
    origin_warehouse = models.ForeignKey(
        "organizations.Warehouse", null=True, blank=True, on_delete=models.SET_NULL, related_name="outbound_shipments"
    )
    destination_warehouse = models.ForeignKey(
        "organizations.Warehouse", null=True, blank=True, on_delete=models.SET_NULL, related_name="inbound_shipments"
    )
    origin_address = models.CharField(max_length=240, blank=True)
    destination_address = models.CharField(max_length=240, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.BOOKED, db_index=True)
    tracking_number = models.CharField(max_length=80, blank=True, db_index=True)
    etd = models.DateTimeField(null=True, blank=True)
    eta = models.DateTimeField(null=True, blank=True)
    atd = models.DateTimeField(null=True, blank=True)
    ata = models.DateTimeField(null=True, blank=True)
    delay_minutes = models.IntegerField(default=60)
    customs_status = models.CharField(max_length=40, default="pending")
    freight_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="USD")
    weight_kg = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    volume_cbm = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    current_location = models.CharField(max_length=160, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "number")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "eta"])]


class Container(TenantModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="containers")
    container_number = models.CharField(max_length=40)
    container_type = models.CharField(max_length=20, default="40HC")
    seal_number = models.CharField(max_length=40, blank=True)
    weight_kg = models.DecimalField(max_digits=12, decimal_places=3, default=0)


class Package(TenantModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="packages")
    container = models.ForeignKey(Container, null=True, blank=True, on_delete=models.SET_NULL, related_name="packages")
    tracking_number = models.CharField(max_length=80, blank=True)
    sku = models.CharField(max_length=64, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=1)
    weight_kg = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    status = models.CharField(max_length=20, default="packed")


class ShipmentMilestone(TenantModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="milestones")
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=120)
    planned_at = models.DateTimeField(null=True, blank=True)
    actual_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=160, blank=True)
    is_missed = models.BooleanField(default=False)
    sequence = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["sequence", "planned_at"]


class TrackingEvent(TenantModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="tracking_events")
    occurred_at = models.DateTimeField()
    status = models.CharField(max_length=40)
    location = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=40, default="manual")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["occurred_at"]


class ProofOfDelivery(TenantModel, AuditedModel):
    shipment = models.OneToOneField(Shipment, on_delete=models.CASCADE, related_name="proof_of_delivery")
    signed_by = models.CharField(max_length=160)
    signed_at = models.DateTimeField()
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to="pod/", blank=True, null=True)
    condition = models.CharField(max_length=40, default="good")


class FreightCost(TenantModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="freight_costs")
    charge_type = models.CharField(max_length=40)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    billed_to = models.CharField(max_length=40, default="shipper")


class Consolidation(TenantModel, AuditedModel):
    number = models.CharField(max_length=40)
    carrier = models.ForeignKey(Carrier, on_delete=models.PROTECT, related_name="consolidations")
    route = models.ForeignKey(Route, null=True, blank=True, on_delete=models.SET_NULL, related_name="consolidations")
    scheduled_departure = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default="open")
    shipments = models.ManyToManyField(Shipment, blank=True, related_name="consolidations")

    class Meta:
        unique_together = ("organization", "number")


class DeliverySchedule(TenantModel):
    warehouse = models.ForeignKey("organizations.Warehouse", on_delete=models.CASCADE, related_name="delivery_windows")
    carrier = models.ForeignKey(Carrier, null=True, blank=True, on_delete=models.SET_NULL, related_name="delivery_windows")
    weekday = models.PositiveSmallIntegerField(default=1)
    window_start = models.TimeField()
    window_end = models.TimeField()
    dock = models.CharField(max_length=40, blank=True)
    capacity = models.PositiveIntegerField(default=10)


class LogisticsException(TenantModel, AuditedModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="exceptions")
    code = models.CharField(max_length=40)
    severity = models.CharField(max_length=20, default="medium")
    description = models.TextField()
    status = models.CharField(max_length=20, default="open")
    resolved_at = models.DateTimeField(null=True, blank=True)
