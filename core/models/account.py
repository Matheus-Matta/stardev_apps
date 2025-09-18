# account/models.py
import uuid
from django.db import models
from django.utils import timezone
from auditlog.registry import auditlog

class Account(models.Model):
    """
    Representa um 'account' (cliente). PK em UUID v4.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID v4
    slug = models.SlugField(unique=True, max_length=80)  # será forçado para lowercase no save()
    legal_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    time_zone = models.CharField(max_length=64, default="America/Sao_Paulo")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = self.slug.lower()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.display_name} ({self.slug})"

auditlog.register(Account)
