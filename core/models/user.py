# account/models_user.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from .account import Account  # o "Account"
from .files import Files
from auditlog.registry import auditlog
from core.utils.normalize_url_media import normalize_url_media

class User(AbstractUser):
    """
    Usuário customizado, com UUID e vínculo a um Account.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="users")
    avatar = models.OneToOneField(Files, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_avatar")
    
    display_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
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
    
    @property
    def avatar_url(self):
        file_field = getattr(self.avatar, "file", None) if getattr(self, "avatar", None) else None
        url = getattr(file_field, "url", None)
        return normalize_url_media(url)
    
auditlog.register(User)