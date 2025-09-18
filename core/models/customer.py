import uuid
from django.db import models
from django.utils import timezone
from auditlog.registry import auditlog

from .account import Account
from .business import Business
from .address import Address
from .contact import Contact

class CustomerType(models.TextChoices):
    PERSON = "person", "Pessoa Física"
    COMPANY = "company", "Pessoa Jurídica"

class AddressRole(models.TextChoices):
    BILLING = "billing", "Cobrança (ERP)"
    SHIPPING = "shipping", "Entrega (TMS/ERP)"
    VISIT   = "visit",   "Visita / Correspondência"
    HOME    = "home",    "Residencial"
    OTHER   = "other",   "Outro"

class PaymentTerm(models.TextChoices):
    CASH = "cash", "À vista"
    NET15 = "net15", "15 dias"
    NET30 = "net30", "30 dias"
    NET45 = "net45", "45 dias"
    NET60 = "net60", "60 dias"

class Customer(models.Model):
    """
    Cliente multi-tenant com dados para ERP/PDV/TMS.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="customers")

    # Identificação
    customer_type = models.CharField(max_length=10, choices=CustomerType.choices, default=CustomerType.PERSON)
    full_name = models.CharField(max_length=255)
    fantasy_name = models.CharField(max_length=255, blank=True, null=True)
    document = models.CharField(max_length=32, blank=True, null=True)  # CPF/CNPJ (sem máscara)
    state_registration = models.CharField(max_length=32, blank=True, null=True)
    municipal_registration = models.CharField(max_length=32, blank=True, null=True)

    # Contatos básicos (campos “primários” opcionais para conveniência)
    primary_email = models.EmailField(blank=True, null=True)
    primary_phone = models.CharField(max_length=32, blank=True, null=True)

    # ERP
    payment_term = models.CharField(max_length=10, choices=PaymentTerm.choices, default=PaymentTerm.CASH)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_blocked = models.BooleanField(default=False)
    notes_erp = models.TextField(blank=True, null=True)

    # PDV
    loyalty_code = models.CharField(max_length=64, blank=True, null=True, unique=True)
    preferred_store = models.ForeignKey(
        Business, on_delete=models.SET_NULL, null=True, blank=True, related_name="preferred_customers"
    )
    marketing_opt_in = models.BooleanField(default=False)
    birth_date = models.DateField(blank=True, null=True)

    # TMS
    delivery_notes = models.TextField(blank=True, null=True)
    delivery_time_window_start = models.TimeField(blank=True, null=True)
    delivery_time_window_end = models.TimeField(blank=True, null=True)
    requires_scheduling = models.BooleanField(default=False)
    unloading_requirements = models.CharField(max_length=255, blank=True, null=True)

    # RELACIONAMENTOS (M2M declarados na própria classe)
    addresses = models.ManyToManyField(
        Address,
        through="CustomerAddress",
        related_name="customers",
        blank=True,
    )
    contacts = models.ManyToManyField(
        "Contact",
        through="CustomerContact",
        related_name="customers",
        blank=True,
    )

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        constraints = [
            models.UniqueConstraint(fields=["Account", "document"], name="uniq_customer_account_document"),
        ]
        indexes = [
            models.Index(fields=["Account", "full_name"]),
            models.Index(fields=["Account", "document"]),
            models.Index(fields=["is_active"]),
        ]
        ordering = ("full_name",)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        if self.document:
            self.document = "".join(filter(str.isalnum, self.document))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.document or 'sem doc'})"

auditlog.register(Customer)

class CustomerAddress(models.Model):
    """
    Tabela 'through' do M2M Customer<->Address com metadados.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer_addresses")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="customer_addresses")

    role = models.CharField(max_length=16, choices=AddressRole.choices, default=AddressRole.SHIPPING)
    is_primary = models.BooleanField(default=False)

    valid_from = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)

    label = models.CharField(max_length=64, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Customer Address"
        verbose_name_plural = "Customer Addresses"
        constraints = [
            models.UniqueConstraint(fields=["customer", "address", "role"], name="uniq_customer_address_role"),
        ]
        indexes = [
            models.Index(fields=["customer", "role", "is_primary"]),
        ]

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} @ {self.address} [{self.role}]"

auditlog.register(CustomerAddress)

class CustomerContact(models.Model):
    """
    Tabela 'through' do M2M Customer<->Contact.
    Guarda metadados do vínculo (ex.: se é principal para aquele cliente).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer_contacts")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="customer_contacts")

    is_primary = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Customer Contact"
        verbose_name_plural = "Customer Contacts"
        constraints = [
            models.UniqueConstraint(fields=["customer", "contact"], name="uniq_customer_contact"),
        ]
        indexes = [
            models.Index(fields=["customer", "is_primary"]),
        ]

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} ⇄ {self.contact} ({'primary' if self.is_primary else 'alt'})"


auditlog.register(CustomerContact)