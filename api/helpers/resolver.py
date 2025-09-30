# api/helpers/resolver.py
from typing import Optional, Type
from django.apps import apps as django_apps
from django.db.models import Model, ForeignKey
from django.utils.module_loading import import_string

class ModelResolver:
    """Resolve modelos, serializers e metadados necessários para as operações."""

    def resolve_model(self, model_name: str) -> Optional[Type[Model]]:
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

    def resolve_serializer_for_model(self, model_cls: Type[Model]):
        """Tenta carregar <app_label>.serializers.<ModelName>Serializer"""
        app_label = model_cls._meta.app_label
        path = f"{app_label}.serializers.{model_cls.__name__}Serializer"
        try:
            return import_string(path)
        except Exception:
            return None

    def find_account_fk_field(self, model_cls: Type[Model]) -> Optional[str]:
        for candidate in ("Account", "account", "tenant", "Tenant"):
            try:
                field = model_cls._meta.get_field(candidate)
                if isinstance(field, ForeignKey):
                    return field.name
            except Exception:
                pass

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
        try:
            if model_cls.__name__.lower() == "account":
                return True
            return str(getattr(model_cls._meta, "label_lower", "")).endswith(".account")
        except Exception:
            return False
