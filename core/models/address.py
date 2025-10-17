# account/models_address.py
import uuid
from django.db import models
from django.utils import timezone
from .account import Account
from simple_history.models import HistoricalRecords
from core.utils.generate_unique_code import generate_unique_code

class Address(models.Model):
    """
    Endereço 'canônico' reutilizável. Pode ser usado por múltiplos clientes (M2M).
    Ideal para normalizar e evitar duplicidade entre módulos.
    """
 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=False, blank=True)
    
    country = models.CharField(max_length=2, default="BR")
    state = models.CharField(max_length=64)
    city = models.CharField(max_length=128)
    district = models.CharField(max_length=128, blank=True, null=True)
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=32, blank=True, null=True)
    complement = models.CharField(max_length=128, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    history = HistoricalRecords()       

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    
    place_id = models.CharField(max_length=128, blank=True, null=True)
    geohash = models.CharField(max_length=16, blank=True, null=True)

    address_json = models.JSONField(default=dict, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="addresses"
    )

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        indexes = [
            models.Index(fields=["country", "state", "city"]),
            models.Index(fields=["postal_code"]),
        ]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code(self, Address, prefix="ADR")
            
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        num = f", {self.number}" if self.number else ""
        city = f" - {self.city}" if self.city else ""
        return f"{self.street}{num}{city}"
