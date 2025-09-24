# account/models_business.py
import uuid
from django.db import models
from django.utils import timezone
from .account import Account
from .address import Address
from auditlog.registry import auditlog

class BusinessType(models.TextChoices):
    COMPANY = "company", "Empresa (HQ)"
    STORE = "store", "Loja"
    WAREHOUSE = "warehouse", "Depósito"
    DC = "dc", "Centro de Distribuição"
    DEPARTMENT = "department", "Departamento"
    OTHER = "other", "Outro"

class Business(models.Model):
    """
    Unidade de negócio (empresa, loja, CD, departamento).
    Ligada a um Account.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="businesses")
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL, related_name="businesses")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    
    code = models.CharField(max_length=80)
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)

    business_type = models.CharField(max_length=20, choices=BusinessType.choices)
    address_json = models.JSONField(default=dict)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Business"
        verbose_name_plural = "Businesses"
        constraints = [
            models.UniqueConstraint(fields=["Account", "code"], name="uniq_business_Account_code"),
        ]

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name} ({self.cnpj})"

auditlog.register(Business)
