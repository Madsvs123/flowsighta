from django.db import models

from apps.core.models import AuditedModel, SoftDeleteModel, TenantModel


class Customer(TenantModel, AuditedModel, SoftDeleteModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        BLACKLISTED = "blacklisted", "Blacklisted"

    code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    country = models.CharField(max_length=80, blank=True)
    credit_limit = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    payment_terms = models.CharField(max_length=80, blank=True)
    is_tax_exempt = models.BooleanField(default=False)

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.name


class CustomerContact(TenantModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=160)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    role = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} · {self.customer.name}"


class CustomerAddress(TenantModel):
    class Type(models.TextChoices):
        BILLING = "billing", "Billing"
        SHIPPING = "shipping", "Shipping"
        REGISTERED = "registered", "Registered"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="addresses")
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.BILLING)
    address = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["customer", "type"]

    def __str__(self):
        return f"{self.customer.name} · {self.type}"


class CustomerAgreement(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        TERMINATED = "terminated", "Terminated"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="agreements")
    title = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    discount_pct = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.name} · {self.title}"
