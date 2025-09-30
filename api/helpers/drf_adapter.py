# api/helpers/drf_adapter.py
from typing import Any, Dict, Optional, Type
from django.db.models import Model, Field, FileField, ImageField
from django.db.models.fields.files import FieldFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .resolver import ModelResolver
from core.utils.normalize_url_media import normalize_url_media
from django.core.files.uploadedfile import UploadedFile
from django.core.files.base import File as DjangoFile
from core.utils.normalize_url_media import normalize_url_media

class FileInfoField(serializers.Field):
    def to_representation(self, value):
        if not isinstance(value, FieldFile) or not value:
            return None
        try:
            url = normalize_url_media(getattr(value, "url", None))
        except Exception:
            url = None
        return {"name": getattr(value, "name", None), "url": url}

    def _coerce_one(self, data):
        if isinstance(data, (UploadedFile, DjangoFile, FieldFile)):
            return data
        if hasattr(data, "read") and hasattr(data, "name"):
            return data
        return None

    def to_internal_value(self, data):
        if data is None or data == "":
            return None

        if isinstance(data, (list, tuple)):
            for item in data:
                coerced = self._coerce_one(item)
                if coerced is not None:
                    return coerced
            raise ValidationError("Formato inválido para arquivo. Envie multipart/form-data com o campo do arquivo.")

        if isinstance(data, dict):
            for key in ("file", "upload", "value"):
                coerced = self._coerce_one(data.get(key))
                if coerced is not None:
                    return coerced
            if any(k in data for k in ("file", "upload", "value")):
                return None
            raise ValidationError("Formato inválido para arquivo. Envie multipart/form-data com o campo do arquivo.")

        coerced = self._coerce_one(data)
        if coerced is not None:
            return coerced

        raise ValidationError("Formato inválido para arquivo. Envie multipart/form-data com o campo do arquivo.")




class DRFSerializerAdapter:
    """
    Serializa/valida usando DRF Serializer.
    - Usa serializer explícito quando disponível.
    - Caso contrário, gera um ModelSerializer dinâmico.
    """

    def __init__(self, resolver: ModelResolver):
        self.resolver = resolver

    def serialize_instance(self, model_name: str, instance: Model, *, context: Optional[dict]=None) -> Optional[Dict[str, Any]]:
        model_cls = self.resolver.resolve_model(model_name)
        if not model_cls or not isinstance(instance, model_cls):
            return None
        SerializerClass = self._resolve_or_build_serializer(model_cls)
        ser = SerializerClass(instance, context=context or {})
        return {
            "model": getattr(model_cls._meta, "label_lower", model_cls.__name__.lower()),
            "id": str(instance.pk),
            "fields": ser.data,
        }

    def create(self, model_name: str, payload: Dict[str, Any], *, context=None) -> Model:
        model_cls = self.resolver.resolve_model(model_name)
        if not model_cls:
            raise ValidationError(f"Modelo '{model_name}' não encontrado.")
        SerializerClass = self._resolve_or_build_serializer(model_cls)
        ser = SerializerClass(data=payload, context=context or {})
        ser.is_valid(raise_exception=True)
        return ser.save()

    def update(self, model_name: str, instance: Model, payload: Dict[str, Any], *, context=None, partial: bool = True) -> Model:
        model_cls = self.resolver.resolve_model(model_name)
        if not model_cls:
            raise ValidationError(f"Modelo '{model_name}' não encontrado.")
        SerializerClass = self._resolve_or_build_serializer(model_cls)
        ser = SerializerClass(instance, data=payload, partial=partial, context=context or {})
        ser.is_valid(raise_exception=True)
        return ser.save()

    def get_serializer_fields(self, model_cls: Type[Model]) -> list[str]:
        SerializerClass = self._resolve_or_build_serializer(model_cls)
        fields = list(SerializerClass().get_fields().keys())
        if "id" not in fields:
            fields.insert(0, "id")
        return fields

    def _resolve_or_build_serializer(self, model_cls):
        explicit = self.resolver.resolve_serializer_for_model(model_cls)
        if explicit:
            return explicit
        return self._build_dynamic_serializer(model_cls)

    def _build_dynamic_serializer(self, model_cls):
        tenant_fk = self.resolver.find_account_fk_field(model_cls)

        class DynamicSerializer(serializers.ModelSerializer):
            class Meta:
                model = model_cls
                fields = "__all__"

            def build_standard_field(self, field_name: str, model_field: Field):
                field_class, field_kwargs = super().build_standard_field(field_name, model_field)
                if isinstance(model_field, (FileField, ImageField)):
                    return FileInfoField, {}
                return field_class, field_kwargs

            def get_fields(self):
                fields = super().get_fields()
                if tenant_fk and tenant_fk in fields:
                    fields.pop(tenant_fk, None) 
                return fields

            def create(self, validated_data):
                if tenant_fk:
                    request = self.context.get("request")
                    account = getattr(request, "account", None) if request else None
                    if account is None:
                        raise ValidationError({"non_field_errors": ["Tenant não identificado."]})
                    try:
                        validated_data[tenant_fk] = account
                    except Exception:
                        validated_data[f"{tenant_fk}_id"] = getattr(account, "id", None)
                return super().create(validated_data)

            def update(self, instance, validated_data):
                if tenant_fk:
                    validated_data.pop(tenant_fk, None)
                    validated_data.pop(f"{tenant_fk}_id", None)
                return super().update(instance, validated_data)

        DynamicSerializer.__name__ = f"{model_cls.__name__}AutoSerializer"
        return DynamicSerializer
