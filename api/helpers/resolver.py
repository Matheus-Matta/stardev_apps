# api/helpers/resolver.py
"""
Responsável por:
- Resolver Model por nome (com ou sem app_label)
- Descobrir o ModelForm associado
- Detectar o campo de Account (FK) no model
- Detectar se o model é a própria Account
"""

from typing import Optional, Type
from django.apps import apps as django_apps
from django.forms import ModelForm
from django.forms import models as model_forms
from django.utils.module_loading import import_string
from django.db.models import Model, ForeignKey


class ModelResolver:
    """Resolve modelos, forms e metadados necessários para as operações."""

    def resolve_model(self, model_name: str) -> Optional[Type[Model]]:
        """
        Retorna a classe do Model a partir de `model_name`.
        Aceita "app.Model" ou apenas "Model" (faz scan em todos os apps).
        """
        name = (model_name or "").strip()
        if not name:
            return None

        if "." in name:
            app_label, model = name.split(".", 1)
            return django_apps.get_model(app_label, model)

        lower = name.lower()
        for m in django_apps.get_models():
            if m.__name__.lower() == lower:
                return m
        return None

    def resolve_form_for_model(self, model_cls: Type[Model]) -> Type[ModelForm]:
        """
        Tenta carregar <app>.forms.<ModelName>Form; senão cria um ModelForm com fields='__all__'.
        """
        app_label = model_cls._meta.app_label
        form_class_path = f"{app_label}.forms.{model_cls.__name__}Form"
        try:
            return import_string(form_class_path)
        except Exception:
            return model_forms.modelform_factory(model=model_cls, fields="__all__")

    def find_account_fk_field(self, model_cls: Type[Model]) -> Optional[str]:
        """
        Detecta o campo FK que referencia Account. Procura por nomes comuns
        ('Account', 'account', 'tenant', 'Tenant') e por referência real à model Account.
        """
        # 1) candidatos por nome
        for candidate in ("Account", "account", "tenant", "Tenant"):
            try:
                field = model_cls._meta.get_field(candidate)
                if isinstance(field, ForeignKey):
                    return field.name
            except Exception:
                pass

        # 2) referência concreta à model Account (quando possível)
        try:
            AccountModel = (
                django_apps.get_model("core", "Account")
                or django_apps.get_model("account", "Account")
            )
        except Exception:
            AccountModel = None

        if AccountModel:
            for field in model_cls._meta.get_fields():
                if isinstance(field, ForeignKey) and getattr(field, "remote_field", None):
                    if field.remote_field.model is AccountModel:
                        return field.name
        return None

    def is_account_model(self, model_cls: Type[Model]) -> bool:
        """
        True se o `model_cls` for Account (independente do app_label).
        """
        try:
            if model_cls.__name__.lower() == "account":
                return True
            return str(getattr(model_cls._meta, "label_lower", "")).endswith(".account")
        except Exception:
            return False
