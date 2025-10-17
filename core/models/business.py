# account/models_business.py
import uuid
from django.db import models
from django.utils import timezone
from .account import Account
from .address import Address
from core.utils.generate_unique_code import generate_unique_code  # Importa o utilitário
from simple_history.models import HistoricalRecords

class BusinessType(models.Model):
    """
    Tipo de unidade de negócio cadastrável.
    Ligada a um Account.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="business_types"
    )

    code = models.CharField(max_length=20, unique=False, blank=True)
    name = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    history = HistoricalRecords()   

    class Meta:
        verbose_name = "Business Type"
        verbose_name_plural = "Business Types"
        constraints = [
            models.UniqueConstraint(
                fields=["Account", "code"], name="uniq_businesstype_Account_code"
            ),
            models.UniqueConstraint(
                fields=["Account", "name"], name="uniq_businesstype_Account_name"
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code(self, BusinessType, prefix="BST")

        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Business(models.Model):
    """
    Unidade de negócio (empresa, loja, CD, departamento).
    Ligada a um Account.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="businesses"
    )
    address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="businesses",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    business_type = models.ForeignKey(
        BusinessType, on_delete=models.PROTECT, related_name="businesses"
    )

    code = models.CharField(max_length=80)
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)
    
    history = HistoricalRecords()   
    class Meta:
        verbose_name = "Business"
        verbose_name_plural = "Businesses"
        constraints = [
            models.UniqueConstraint(
                fields=["Account", "code"], name="uniq_business_Account_code"
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code(self, Business, prefix="BUS")

        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name} ({self.cnpj})"
