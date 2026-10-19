from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class Supplier(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        PROSPECT = "prospect", "Prospect"
        ONBOARDING = "onboarding", "Onboarding"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        BLOCKED = "blocked", "Blocked"

    class Risk(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    legal_name = models.CharField(max_length=240, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    risk_level = models.CharField(max_length=20, choices=Risk.choices, default=Risk.HIGH, db_index=True)
    category = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=120, blank=True)
    address_line1 = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    tax_id = models.CharField(max_length=64, blank=True)
    payment_terms = models.CharField(max_length=40, default="Net 30")
    currency = models.CharField(max_length=8, default="USD")
    default_lead_time_days = models.PositiveIntegerField(default=14)
    minimum_order_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fill_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_spend = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    preferred = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "code")
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "status", "risk_level"])]

    def __str__(self):
        return f"{self.code} {self.name}"


class SupplierContact(TenantModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="contact")
    name = models.CharField(max_length=160)
    title = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    is_primary = models.BooleanField(default=False)
    role = models.CharField(max_length=80, blank=True)


class SupplierContract(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        TERMINATED = "terminated", "Terminated"

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="contracts")
    number = models.CharField(max_length=60)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    payment_terms = models.CharField(max_length=40, blank=True)
    incoterms = models.CharField(max_length=20, blank=True)
    auto_renew = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "number")


class SupplierProduct(TenantModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="products")
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uom = models.CharField(max_length=20, default="EA")
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    currency = models.CharField(max_length=8, default="USD")
    lead_time_days = models.PositiveIntegerField(default=14)
    moq = models.PositiveIntegerField(default=1)
    order_multiple = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    catalog_product_id = models.UUIDField(null=True, blank=True)

    class Meta:
        unique_together = ("supplier", "sku")


class SupplierCertification(TenantModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=160)
    issuer = models.CharField(max_length=160, blank=True)
    certificate_number = models.CharField(max_length=80, blank=True)
    issued_on = models.DateField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default="valid")
    document_url = models.URLField(blank=True)


class SupplierDocument(TenantModel, AuditedModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=40, default="other")
    file = models.FileField(upload_to="suppliers/docs/", blank=True, null=True)
    notes = models.TextField(blank=True)


class OnboardingStep(TenantModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="onboarding_steps")
    sequence = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="pending")
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    owner_name = models.CharField(max_length=160, blank=True)


class SupplierScoreSnapshot(TenantModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="score_snapshots")
    period_start = models.DateField()
    period_end = models.DateField()
    on_time_delivery = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    quality = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fill_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    lead_time_variance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    composite_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    spend = models.DecimalField(max_digits=16, decimal_places=2, default=0)


class PurchaseHistory(TenantModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="purchase_history")
    purchase_order_number = models.CharField(max_length=40)
    ordered_on = models.DateField()
    received_on = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="USD")
    on_time = models.BooleanField(default=True)
    notes = models.CharField(max_length=240, blank=True)
