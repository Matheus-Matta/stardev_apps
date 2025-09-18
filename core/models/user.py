# account/models_user.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from .account import Account  # o "Account"
from auditlog.registry import auditlog

class User(AbstractUser):
    """
    Usuário customizado, com UUID e vínculo a um Account.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="users")

    # campos extras opcionais
    display_name = models.CharField(max_length=255, blank=True, null=True)

    # campos do AbstractUser: username, email, password, is_active, is_staff, is_superuser...
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    EXPORT_EXCLUDE = ["password", "is_staff"]
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        constraints = [
            models.UniqueConstraint(fields=["Account", "username"], name="uniq_Account_username"),
        ]

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} @ {self.Account.slug}"
    
auditlog.register(User)