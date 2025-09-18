import uuid
from django.db import models
from django.utils import timezone
from auditlog.registry import auditlog
from .account import Account

class ContactType(models.TextChoices):
    EMAIL = "email", "Email"
    MOBILE = "mobile", "Celular"
    WHATSAPP = "whatsapp", "WhatsApp"
    PHONE = "phone", "Telefone"
    OTHER = "other", "Outro"

class Contact(models.Model):
    """
    Entidade de contato reutilizável.
    Pode ser compartilhada por múltiplos clientes (ex.: mesmo e-mail/telefone).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=16, choices=ContactType.choices, default=ContactType.MOBILE)
    value = models.CharField(max_length=255)  # email/telefone/etc.
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="contacts")
    
    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        indexes = [
            models.Index(fields=["type", "value"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["type", "value"], name="uniq_contact_type_value"),
        ]

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type}: {self.value}"


auditlog.register(Contact)