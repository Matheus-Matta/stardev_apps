# account/signals_groups.py
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from core.models import AccountGroup

User = get_user_model()

@receiver(m2m_changed, sender=User.groups.through)
def enforce_same_account_group(sender, instance: User, action, reverse, model, pk_set, **kwargs):
    """
    Bloqueia adicionar grupos de outro Account ao usuário.
    """
    if action != "pre_add" or reverse or not pk_set:
        return

    user_account_id = getattr(instance, "Account_id", None)
    if not user_account_id:
        return

    allowed_ids = set(
        AccountGroup.objects
        .filter(account_id=user_account_id)
        .values_list("group_id", flat=True)
    )
    invalid = set(pk_set) - allowed_ids
    if invalid:
        raise ValidationError("Grupo não pertence a este Account.")
