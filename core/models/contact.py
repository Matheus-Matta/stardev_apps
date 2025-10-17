import re
import uuid
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .account import Account
from simple_history.models import HistoricalRecords

class ContactType(models.Model):
    """
    Cadastro de tipos de contato, com regex de validação.
    Multi-tenant (por Account) + histórico.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="contact_types"
    )
    name = models.CharField(
        max_length=64, help_text="Nome visível (ex.: Email, Celular, WhatsApp)."
    )
    pattern = models.CharField(
        max_length=255,
        help_text=r"Regex para validar o valor (use âncoras ^ $ se quiser casar tudo).",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    history = HistoricalRecords()   

    class Meta:
        verbose_name = "Contact Type"
        verbose_name_plural = "Contact Types"

    def clean(self):
        try:
            re.compile(self.pattern)
        except re.error as e:
            raise ValidationError({"pattern": f"Regex inválido: {e}"})

        if self.example:
            if re.fullmatch(self.pattern, self.example) is None:
                raise ValidationError(
                    {"example": "Exemplo não casa com o regex informado."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class Contact(models.Model):
    """
    Entidade de contato reutilizável. Validação do 'value' via regex do ContactType.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    contact_type = models.ForeignKey(
        ContactType,
        on_delete=models.PROTECT,
        related_name="contacts",
    )

    value = models.CharField(max_length=255, help_text="email/telefone/etc.")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="contacts"
    )

    history = HistoricalRecords()   

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        indexes = [
            models.Index(fields=["account", "contact_type"]),
            models.Index(fields=["contact_type", "value"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["account", "contact_type", "value"],
                name="uniq_contact_account_type_value",
            ),
        ]

    def clean(self):
        if self.contact_type and self.value:
            pattern = self.contact_type.pattern
            try:
                if re.fullmatch(pattern, self.value) is None:
                    raise ValidationError(
                        {"value": "Valor não corresponde ao padrão do tipo de contato."}
                    )
            except re.error as e:
                raise ValidationError({"contact_type": f"Regex do tipo inválido: {e}"})

        if self.contact_type and self.account_id != self.contact_type.account_id:
            raise ValidationError(
                {"contact_type": "Tipo de contato pertence a outro Account."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.contact_type.code}: {self.value}"
