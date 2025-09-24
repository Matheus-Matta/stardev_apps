# api/helpers/operations.py
"""
Operações com polimorfismo:
- BaseOperation: comportamento comum (sanitize payload, validação, save com transaction)
- CreateOperation / UpdateOperation: especializações
"""

from typing import Dict, Any, Type
from django.db import transaction
from django.db.models import Model
from django.forms import ModelForm
from django.forms.models import model_to_dict
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from .resolver import ModelResolver
from .tenancy import AccountScope
from .errors import ErrorBuilder, UniqueErrorParser


class BaseOperation:
    """Base para operações que usam ModelForm com validação e transação."""

    def __init__(self, request, resolver: ModelResolver, scope: AccountScope, errors: ErrorBuilder, unique: UniqueErrorParser):
        self.request = request
        self.resolver = resolver
        self.scope = scope
        self.errors = errors
        self.unique = unique

    def _sanitize_payload(self, payload: Dict[str, Any], model_cls: Type[Model]) -> Dict[str, Any]:
        """Remove campos sensíveis de tenant do payload."""
        out = dict(payload or {})
        account_field = self.resolver.find_account_fk_field(model_cls)
        for k in ("Account", "account", account_field, f"{account_field}_id"):
            out.pop(k, None)
        return out

    def _bind_form(self, FormClass: Type[ModelForm], instance: Model, data: Dict[str, Any]) -> ModelForm:
        """Cria um ModelForm com os dados informados e arquivos da request."""
        return FormClass(
            data=data,
            files=getattr(self.request, "FILES", None),
            instance=instance,
        )

    def _save_form(self, form: ModelForm, model_cls: Type[Model], account_field: str | None) -> Model:
        """Valida e salva o formulário dentro de transaction; força tenant e trata UNIQUE."""
        if not form.is_valid():
            self.errors.raise_form_validation_error(form)

        try:
            with transaction.atomic():
                obj = form.save(commit=False)
                if account_field:
                    self.scope.ensure_account_on_instance(obj, account_field)
                obj.save()
                if hasattr(form, "save_m2m"):
                    form.save_m2m()
                return obj
        except IntegrityError as ie:
            self.unique.raise_unique_validation_error(model_cls, ie)

    def run(self, model_name: str, **kwargs) -> Dict[str, Any] | None:  # pragma: no cover
        """Executa a operação e retorna o dicionário serializado (ou None)."""
        raise NotImplementedError


class CreateOperation(BaseOperation):
    """Criação de registros."""

    def run(self, model_name: str, payload: Dict[str, Any]) -> Dict[str, Any] | None:
        """Cria um registro do model informado e retorna o serializado."""
        model_cls = self.resolver.resolve_model(model_name)
        if not model_cls:
            raise ValidationError("Modelo inexistente.")

        if self.resolver.is_account_model(model_cls):
            raise ValidationError("Criação de Account não é permitida neste endpoint.")

        account_field = self.resolver.find_account_fk_field(model_cls)
        data = self._sanitize_payload(payload, model_cls)
        FormClass = self.resolver.resolve_form_for_model(model_cls)

        instance = model_cls()
        if account_field:
            self.scope.ensure_account_on_instance(instance, account_field)

        form = self._bind_form(FormClass, instance, data)
        return self._save_form(form, model_cls, account_field)


class UpdateOperation(BaseOperation):
    """Atualização de registros."""

    def run(self, model_name: str, pk: Any, payload: Dict[str, Any]) -> Dict[str, Any] | None:
        """Atualiza o registro indicado pelo pk e retorna o objeto salvo."""
        model_cls = self.resolver.resolve_model(model_name)
        if not model_cls:
            raise ValidationError("Modelo inexistente.")

        qs = self.scope.get_queryset(model_cls)
        if qs is None:
            return None
        obj = qs.filter(pk=pk).first()
        if not obj:
            return None

        account_field = self.resolver.find_account_fk_field(model_cls)
        safe_payload = self._sanitize_payload(payload, model_cls)
        FormClass = self.resolver.resolve_form_for_model(model_cls)

        # merge para contemplar required fields não enviados
        base_data = model_to_dict(obj)
        merged = {**base_data, **safe_payload}

        form = self._bind_form(FormClass, obj, merged)
        return self._save_form(form, model_cls, account_field)
