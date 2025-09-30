# account/models.py
import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
from auditlog.registry import auditlog
from django.contrib.auth.models import Group

class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=80)
    legal_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    time_zone = models.CharField(max_length=64, default="America/Sao_Paulo")

    email_principal = models.EmailField(null=True, blank=True)
    phone_principal = models.CharField(max_length=32, null=True, blank=True)
    site_url = models.URLField(null=True, blank=True, validators=[URLValidator()])

    logo_url = models.URLField(null=True, blank=True, help_text="URL do logo para UI/PDV.")

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

class AccountGroup(models.Model):
    """
    Envolve o auth.Group e o amarra a um Account.
    Cada auth.Group pertence a exatamente 1 Account.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="account_groups"
    )
    group = models.OneToOneField(
        Group, on_delete=models.CASCADE, related_name="account_bind"
    )

    name = models.CharField(max_length=150)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Account Group"
        verbose_name_plural = "Account Groups"
        constraints = [
            models.UniqueConstraint(fields=["account", "name"], name="uniq_account_group_name"),
        ]
        indexes = [
            models.Index(fields=["account", "name"]),
        ]

    def __str__(self):
        return f"{self.account.slug}:{self.name}"

    @property
    def django_group_name(self) -> str:
        return f"{self.account.slug}:{self.name}"

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
        if self.group and self.group.name != self.django_group_name:
            self.group.name = self.django_group_name
            self.group.save(update_fields=["name"])

    @classmethod
    def create_with_group(cls, *, account: Account, name: str) -> "AccountGroup":
        """
        Cria o auth.Group (com nome prefixado) e o AccountGroup de uma vez.
        """
        full = f"{account.slug}:{name}"
        dj_group, _ = Group.objects.get_or_create(name=full)
        obj, _ = cls.objects.get_or_create(account=account, group=dj_group, defaults={"name": name})
        if obj.name != name:
            obj.name = name
            obj.save(update_fields=["name"])
        return obj

auditlog.register(AccountGroup)
auditlog.register(Account)
