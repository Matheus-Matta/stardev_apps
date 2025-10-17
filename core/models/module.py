# account/models_module.py
import uuid
from django.db import models
from django.utils import timezone
from .account import Account   

class ModuleType(models.TextChoices):
    CORE = "CORE", "Recursos Básicos"
    TMS  = "TMS",  "Controle de Transporte"
    PDV  = "PDV",  "Ponto de Venda"
    ERP  = "ERP",  "Gestão de Recursos Empresariais"
    WMS  = "WMS",  "Controle de Estoque"

class AccountModule(models.Model):
    """
    Habilita um módulo fixo (TMS, PDV, ERP, WMS) para um Account (Account).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="modules")
    module = models.CharField(max_length=10, choices=ModuleType.choices)
    features = models.JSONField(default=dict)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Account Module"
        verbose_name_plural = "Account Modules"
        constraints = [
            models.UniqueConstraint(fields=["account", "module"], name="uniq_account_module"),
        ]

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account.slug}::{self.module}"