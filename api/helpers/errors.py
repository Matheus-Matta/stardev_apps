# api/helpers/errors.py
"""
Padroniza o lançamento de erros de validação (DRF ValidationError)
e tenta mapear IntegrityError para mensagens por campo (UNIQUE).
"""

import re
from typing import Optional, Dict, Any, Type
from django.db import IntegrityError
from django.forms import ModelForm
from rest_framework.exceptions import ValidationError
from django.db.models import Model


class ErrorBuilder:
    """Constroi e lança ValidationError no formato esperado pela api."""

    def errors_to_text(self, form: ModelForm) -> str:
        """
        Converte form.errors em string amigável para humanos.
        """
        try:
            parts = []
            for field, errors in form.errors.items():
                for err in errors:
                    parts.append(f"{field}: {err}")
            try:
                for err in form.non_field_errors():
                    parts.append(str(err))
            except Exception:
                pass
            return "; ".join(parts) if parts else "Dados inválidos."
        except Exception:
            return "Dados inválidos."

    def raise_form_validation_error(self, form: ModelForm, default_detail: str = "Dados inválidos."):
        """
        Lança DRF ValidationError com payload contendo:
          - detail (string agregada)
          - errors (dict por campo; cada valor pode ser lista de {message})
        """
        text = self.errors_to_text(form)
        try:
            json_errors = form.errors.get_json_data()
        except Exception:
            json_errors = {}
            for k, v in form.errors.items():
                if isinstance(v, (list, tuple)):
                    json_errors[k] = [{"message": str(x)} for x in v]
                else:
                    json_errors[k] = [{"message": str(v)}]

        raise ValidationError({
            "ok": False,
            "detail": text or default_detail,
            "errors": json_errors,
        })


class UniqueErrorParser:
    """Tenta extrair o campo da UNIQUE constraint a partir da mensagem do banco."""

    KEY_COL_RE = re.compile(r'Key \((?P<col>[a-zA-Z0-9_]+)\)=')
    SQLITE_RE = re.compile(r'UNIQUE constraint failed:\s*[\w"]+\.(?P<col>[a-zA-Z0-9_]+)')
    CNAME_RE  = re.compile(r'unique constraint "(?P<cname>[^"]+)"', re.IGNORECASE)

    def extract_field(self, err: IntegrityError, model_cls: Type[Model]) -> Optional[str]:
        """
        Faz um best-effort para descobrir o nome da coluna.
        """
        msg = str(err) or ""

        m = self.KEY_COL_RE.search(msg)
        if m:
            return m.group("col")

        m = self.SQLITE_RE.search(msg)
        if m:
            return m.group("col")

        m = self.CNAME_RE.search(msg)
        if m:
            cname = m.group("cname")
            parts = cname.split("_")
            if len(parts) >= 3:
                possible_field = parts[-2]
                try:
                    model_cls._meta.get_field(possible_field)
                    return possible_field
                except Exception:
                    pass

        for f in model_cls._meta.get_fields():
            try:
                if getattr(f, "unique", False) and re.search(rf'\b{re.escape(f.name)}\b', msg):
                    return f.name
            except Exception:
                pass
        return None

    def raise_unique_validation_error(self, model_cls: Type[Model], err: IntegrityError):
        """
        Lança ValidationError com mapeamento por campo quando possível.
        """
        field = self.extract_field(err, model_cls)
        if field:
            raise ValidationError({
                "ok": False,
                "detail": f"{field}: já existe um registro com este valor.",
                "errors": { field: [{"message": "Já existe um registro com este valor."}] }
            })
        raise ValidationError({
            "ok": False,
            "detail": "Violação de unicidade.",
            "errors": { "non_field_errors": [{"message": "Violação de unicidade."}] }
        })
