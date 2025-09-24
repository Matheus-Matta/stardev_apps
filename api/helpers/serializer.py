# api/helpers/serializer.py
"""
Serializa instâncias usando o ModelForm do model, respeitando fields e tipos (FK/M2M/File).
"""

from typing import Dict, Any, Optional, Type
from datetime import date, datetime
from django.db.models import Model, ForeignKey, ManyToManyField, FileField, ImageField
from django.forms import ModelForm
from django.forms import models as model_forms
from django.db.models.fields.files import FieldFile
from rest_framework.exceptions import ValidationError
from core.utils.normalize_url_media import normalize_url_media
from .resolver import ModelResolver


class FormSerializer:
    """Serializa instâncias usando o formulário do model (fields = contrato da API)."""

    def __init__(self, resolver: ModelResolver):
        self.resolver = resolver

    def serialize_using_form(self, model_name: str, instance: Model) -> Optional[Dict[str, Any]]:
        """
        Constrói um dicionário contendo:
          - model: label_lower do model
          - id: PK (string)
          - fields: { nome_do_campo: valor_serializado }
        Somente os fields definidos no ModelForm são incluídos.
        """
        try:
          model_cls = self.resolver.resolve_model(model_name)
          if not model_cls or not isinstance(instance, model_cls):
              return None

          FormClass: Type[ModelForm] = self.resolver.resolve_form_for_model(model_cls)
          form = FormClass(instance=instance)

          data: Dict[str, Any] = {
              "model": getattr(model_cls._meta, "label_lower", model_cls.__name__.lower()),
              "id": str(instance.pk),
              "fields": {},
          }

          for name, field in form.fields.items():
              value = getattr(instance, name, None)

              try:
                  model_field = model_cls._meta.get_field(name)
              except Exception:
                  model_field = None

              if value in (None, ""):
                  initial = getattr(field, "initial", None)
                  if initial not in (None, ""):
                      value = initial
                  else:
                      try:
                          bound = form[name]
                          bv = bound.value()
                          if bv not in (None, ""):
                              value = bv
                      except Exception:
                          pass

              if isinstance(model_field, ManyToManyField):
                  data["fields"][name] = list(getattr(instance, name).values_list("pk", flat=True))
                  continue

              if isinstance(model_field, ForeignKey):
                  data["fields"][name] = getattr(value, "pk", None)
                  continue

              if isinstance(model_field, (FileField, ImageField)):
                  ff: FieldFile = getattr(instance, name, None)
                  if isinstance(ff, FieldFile) and ff:
                      try:
                          url = normalize_url_media(getattr(ff, "url", None))
                      except Exception:
                          url = None
                      data["fields"][name] = {"name": getattr(ff, "name", None), "url": url}
                  else:
                      data["fields"][name] = None
                  continue

              if isinstance(value, (datetime, date)):
                  data["fields"][name] = value.isoformat()
                  continue

              data["fields"][name] = value

          return data

        except Exception as e:
          raise ValidationError(str(e))
