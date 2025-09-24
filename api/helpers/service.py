# api/helpers/service.py
"""
ModelService: orquestra as operações, compondo Resolver, Scope, Errors, Serializer e Operations.
Mantém métodos “amigáveis” para a camada de views.
"""

from typing import Optional, Any, Dict, Type
from django.db.models import Model, QuerySet
from rest_framework.exceptions import ValidationError
from .resolver import ModelResolver
from .tenancy import AccountScope
from .errors import ErrorBuilder, UniqueErrorParser
from .serializer import FormSerializer
from .operations import CreateOperation, UpdateOperation


class ModelService:
    """
    Fachada interna usada por ModelHelper. Encapsula componentes e oferece métodos
    de alto nível (create/update/delete/get/serialize).
    """

    def __init__(self, request):
        """Cria os componentes necessários para as operações."""
        self.request = request
        self.resolver = ModelResolver()
        self.scope = AccountScope(request, self.resolver)
        self.errors = ErrorBuilder()
        self.unique = UniqueErrorParser()
        self.serializer = FormSerializer(self.resolver)

    # ---------- Leitura ----------
    def get_queryset(self, model_name: str) -> Optional[QuerySet]:
        """Retorna o queryset já escopado pelo tenant, quando aplicável."""
        model_cls = self.resolver.resolve_model(model_name)
        if not model_cls:
            return None
        return self.scope.get_queryset(model_cls)

    def get_one(self, model_name: str, pk: Any) -> Optional[Model]:
        """Retorna uma única instância filtrada pelo escopo do tenant."""
        qs = self.get_queryset(model_name)
        if qs is None:
            return None
        return qs.filter(pk=pk).first() or None

    def get_one_serialized(self, model_name: str, pk: Any) -> Optional[Dict[str, Any]]:
        """Serializa a instância localizada pelo pk via ModelForm do model."""
        instance = self.get_one(model_name, pk)
        if not instance:
            return None
        return self.serializer.serialize_using_form(model_name, instance)

    # ---------- Escrita ----------
    def create_one(self, model_name: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria um registro e devolve o dicionário serializado (fields do ModelForm)."""
        op = CreateOperation(self.request, self.resolver, self.scope, self.errors, self.unique)
        obj = op.run(model_name, payload=payload)
        if not obj:
            return None
        return self.serializer.serialize_using_form(model_name, obj)

    def update_one(self, model_name: str, pk: Any, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um registro e devolve o dicionário serializado (fields do ModelForm)."""
        op = UpdateOperation(self.request, self.resolver, self.scope, self.errors, self.unique)
        obj = op.run(model_name, pk=pk, payload=payload)
        if not obj:
            return None
        return self.serializer.serialize_using_form(model_name, obj)

    def delete_one(self, model_name: str, pk: Any) -> bool:
        """Deleta a instância indicada (respeitando o escopo do tenant)."""
        model_cls = self.resolver.resolve_model(model_name)
        if not model_cls:
            return False

        user = getattr(self.request, "user", None)
        is_super = bool(getattr(user, "is_superuser", False))

        # impedir delete de Account se não for super
        if self.resolver.is_account_model(model_cls) and not is_super:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Sem permissão para deletar Account.")

        qs = self.scope.get_queryset(model_cls)
        if qs is None:
            return False

        obj = qs.filter(pk=pk).first()
        if not obj:
            return False

        obj.delete()
        return True
