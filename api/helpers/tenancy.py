# api/helpers/tenancy.py
"""
Lida com escopo de tenant (Account) e aplica restrições no queryset e na instância.
"""

from typing import Optional, Any, Type
from django.core.exceptions import PermissionDenied
from django.db.models import Model, QuerySet
from .resolver import ModelResolver


class AccountScope:
    """Aplica o escopo de tenant/Account nas buscas e atribuições."""

    def __init__(self, request, resolver: ModelResolver):
        """
        Guarda a request, o resolver e dados úteis (account e account_id).
        """
        self.request = request
        self.resolver = resolver
        self.account = getattr(request, "account", None)
        self.account_id: Optional[Any] = getattr(self.account, "id", None)

    def get_queryset(self, model_cls: Type[Model]) -> Optional[QuerySet]:
        """
        Retorna o queryset filtrado por tenant, quando aplicável.
        """
        user = getattr(self.request, "user", None)
        is_super = bool(getattr(user, "is_superuser", False))

        if self.resolver.is_account_model(model_cls):
            if is_super:
                return model_cls.objects.all()
            if not self.account_id:
                return None
            return model_cls.objects.filter(pk=self.account_id)

        account_field = self.resolver.find_account_fk_field(model_cls)
        if not account_field:
            return model_cls.objects.all() if is_super else None

        if is_super:
            return model_cls.objects.all()

        if not self.account_id:
            return None

        return model_cls.objects.filter(**{f"{account_field}_id": self.account_id})

    def ensure_account_on_instance(self, instance: Model, account_field: str):
        """
        Garante que a instância (create/update) tenha o tenant correto.
        """
        if not self.account_id:
            raise PermissionDenied("Contexto de Account ausente em request.account.")
        setattr(instance, f"{account_field}_id", self.account_id)
