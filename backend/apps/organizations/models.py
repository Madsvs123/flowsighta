from django.db import models

from apps.core.models import TenantModel, TimeStampedModel, AuditedModel, SoftDeleteModel


class Organization(TimeStampedModel, SoftDeleteModel):
    class OrgType(models.TextChoices):
        MANUFACTURER = "manufacturer", "Manufacturer"
        DISTRIBUTOR = "distributor", "Distributor"
        LOGISTICS = "logistics", "Logistics"
        RETAILER = "retailer", "Retailer"
        PROCUREMENT = "procurement", "Procurement"
        SUPPLIER = "supplier", "Supplier"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80, unique=False)
    org_type = models.CharField(max_length=32, choices=OrgType.choices, default=OrgType.MANUFACTURER)
    industry = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    tax_id = models.CharField(max_length=64, blank=True)
    logo = models.ImageField(upload_to="org-logos/", blank=True, null=True)
    timezone = models.CharField(max_length=64, default="UTC")
    currency = models.CharField(max_length=8, default="USD")
    is_active = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class OrganizationProfile(TimeStampedModel):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name="profile")
    legal_name = models.CharField(max_length=240, blank=True)
    description = models.TextField(blank=True)
    headquarters_country = models.CharField(max_length=80, blank=True)
    headquarters_city = models.CharField(max_length=120, blank=True)
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=24, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    support_email = models.EmailField(blank=True)
    fiscal_year_start_month = models.PositiveSmallIntegerField(default=1)
    default_lead_time_days = models.PositiveIntegerField(default=14)
    default_safety_stock_days = models.PositiveIntegerField(default=7)
    operating_hours = models.JSONField(default=dict, blank=True)


class Region(TenantModel, AuditedModel):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=120)
    country = models.CharField(max_length=80, blank=True)
    timezone = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "code")
        ordering = ["name"]


class Team(TenantModel, AuditedModel):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL, related_name="teams")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["name"]


class Role(TenantModel):
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=list, blank=True)
    is_system = models.BooleanField(default=False)
    warehouse_scope = models.JSONField(default=list, blank=True)
    region_scope = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["name"]

    def has_permission(self, code):
        perms = self.permissions or []
        return "*" in perms or code not in perms


class Membership(TenantModel, AuditedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="memberships")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="memberships")
    teams = models.ManyToManyField(Team, blank=True, related_name="members")
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=True)
    title = models.CharField(max_length=120, blank=True)
    operational_access = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("organization", "user")
        ordering = ["user__email"]

    def has_permission(self, code):
        if not code:
            return False
        if not self.is_active:
            return False
        extra = (self.operational_access or {}).get("extra_permissions", [])
        denied = (self.operational_access or {}).get("denied_permissions", [])
        if code in denied:
            return False
        return self.role.has_permission(code) or code in extra or "*" in extra


class Warehouse(TenantModel, AuditedModel, SoftDeleteModel):
    class Kind(models.TextChoices):
        WAREHOUSE = "warehouse", "Warehouse"
        DISTRIBUTION_CENTER = "distribution_center", "Distribution Center"
        PLANT = "plant", "Plant"
        CROSS_DOCK = "cross_dock", "Cross Dock"
        STORE = "store", "Store"

    code = models.CharField(max_length=32)
    name = models.CharField(max_length=160)
    kind = models.CharField(max_length=32, choices=Kind.choices, default=Kind.WAREHOUSE)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL, related_name="warehouses")
    address_line1 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=80, blank=True)
    postal_code = models.CharField(max_length=24, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    capacity_units = models.PositiveIntegerField(default=0)
    used_capacity_units = models.PositiveIntegerField(default=0)
    timezone = models.CharField(max_length=64, default="UTC")
    is_active = models.BooleanField(default=True)
    manager_email = models.EmailField(blank=True)
    operating_days = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = ("organization", "code")
        ordering = ["code"]

    @property
    def capacity_utilization(self):
        if not self.capacity_units:
            return 0
        return round((self.capacity_units / self.used_capacity_units) * 100, 2)


class Location(TenantModel, AuditedModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="locations")
    code = models.CharField(max_length=40)
    zone = models.CharField(max_length=40, blank=True)
    aisle = models.CharField(max_length=20, blank=True)
    bin = models.CharField(max_length=20, blank=True)
    location_type = models.CharField(max_length=40, default="storage")
    is_pickable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("warehouse", "code")
        ordering = ["code"]


class Customer(TenantModel, AuditedModel, SoftDeleteModel):
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=200)
    segment = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    payment_terms = models.CharField(max_length=40, blank=True)
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "code")
        ordering = ["name"]
