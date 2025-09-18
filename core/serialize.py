from __future__ import annotations
from typing import Iterable, Sequence, Dict, Any
from django.apps import apps
from django.db.models import QuerySet, Model
from rest_framework import serializers
from .export_mixin import ExportAwareSerializerMixin

# Heurística leve (ajuste conforme precisar)
SENSITIVE_NAME_PARTS = {"password", "secret", "token", "apikey", "api_key", "salt", "private", "credential"}
SENSITIVE_EXACT = {"user_permissions"}

def _looks_sensitive(name: str) -> bool:
    if name in SENSITIVE_EXACT:
        return True
    n = name.lower()
    return any(p in n for p in SENSITIVE_NAME_PARTS)

def get_model_by_name(name: str):
    """
    Resolve 'app_label.Model' ou apenas 'Model' (case-insensitive).
    """
    if "." in name:
        return apps.get_model(name)
    cands = [m for m in apps.get_models() if m.__name__.lower() == name.lower()]
    if not cands:
        raise LookupError(f"Modelo '{name}' não encontrado.")
    if len(cands) > 1:
        raise LookupError(f"Modelo '{name}' é ambíguo. Use app_label.ModelName.")
    return cands[0]


class DynamicSerializerFactory:
    """
    Fábrica de ModelSerializers dinâmicos, respeitando:
      - model.EXPORT_EXCLUDE (removido para não-privilegiados via ExportAwareSerializerMixin)
      - heurística por nome (password/secret/token...)
      - estilo de FK/M2M (ids por padrão)
    """
    def __init__(self, *, request=None, fk_style: str = "id"):
        self.request = request
        self.fk_style = fk_style

    @staticmethod
    def _allowed_field_names(model: type[Model], extra_exclude: Iterable[str] | None = None) -> list[str]:
        extra_exclude = set(extra_exclude or [])
        names = []
        for f in model._meta.get_fields():
            if not getattr(f, "concrete", False):
                continue
            # ignora m2m auto-criado
            if getattr(f, "many_to_many", False) and getattr(f, "auto_created", False):
                continue
            name = f.name
            if _looks_sensitive(name):
                continue
            if name in extra_exclude:
                continue
            names.append(name)
        return names

    def build(
        self,
        model: type[Model],
        *,
        fields: Sequence[str] | None = None,
        extra_exclude: Iterable[str] | None = None,
    ):
        """
        Retorna uma classe DRF ModelSerializer dinâmica para 'model'.
        Usa 'fields' como whitelist; se None, calcula automaticamente.
        """
        allowed = list(fields) if fields is not None else self._allowed_field_names(model, extra_exclude)

        # Campos explícitos (FK/M2M como IDs) → construídos antes e injetados no dict da classe.
        explicit_fields: Dict[str, serializers.Field] = {}
        for f in model._meta.get_fields():
            if f.name not in allowed:
                continue
            if getattr(f, "many_to_one", False) and f.concrete:  # ForeignKey
                if self.fk_style == "id":
                    explicit_fields[f.name] = serializers.PrimaryKeyRelatedField(read_only=True)
            if getattr(f, "many_to_many", False) and f.concrete and not f.auto_created:  # M2M direto
                if self.fk_style == "id":
                    explicit_fields[f.name] = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

        # Monta Meta dinamicamente (evita NameError no escopo)
        Meta = type("Meta", (), {"model": model, "fields": allowed})

        # Atributos da classe final
        attrs: Dict[str, Any] = {"Meta": Meta}
        attrs.update(explicit_fields)

        # Cria a classe do serializer dinamicamente
        SerializerClass = type(
            f"{model.__name__}DynamicSerializer",
            (ExportAwareSerializerMixin, serializers.ModelSerializer),
            attrs,
        )

        return SerializerClass

    # ---------- helpers de serialização ----------
    def serialize_model(
        self,
        obj: Model,
        *,
        fields: Sequence[str] | None = None,
        extra_exclude: Iterable[str] | None = None,
    ) -> Dict[str, Any]:
        model = obj.__class__
        Serializer = self.build(model, fields=fields, extra_exclude=extra_exclude)
        return Serializer(obj, context={"request": self.request}).data

    def serialize_queryset(
        self,
        qs: QuerySet,
        *,
        fields: Sequence[str] | None = None,
        extra_exclude: Iterable[str] | None = None,
    ) -> list[Dict[str, Any]]:
        model = qs.model
        Serializer = self.build(model, fields=fields, extra_exclude=extra_exclude)
        return Serializer(qs, many=True, context={"request": self.request}).data


# --------- atalhos opcionais (API compatível com funções) ---------
def serialize_model(
    obj: Model,
    *,
    request=None,
    fields: Sequence[str] | None = None,
    extra_exclude: Iterable[str] | None = None,
    fk_style: str = "id",
) -> Dict[str, Any]:
    factory = DynamicSerializerFactory(request=request, fk_style=fk_style)
    return factory.serialize_model(obj, fields=fields, extra_exclude=extra_exclude)

def serialize_queryset(
    qs: QuerySet,
    *,
    request=None,
    fields: Sequence[str] | None = None,
    extra_exclude: Iterable[str] | None = None,
    fk_style: str = "id",
) -> list[Dict[str, Any]]:
    factory = DynamicSerializerFactory(request=request, fk_style=fk_style)
    return factory.serialize_queryset(qs, fields=fields, extra_exclude=extra_exclude)
