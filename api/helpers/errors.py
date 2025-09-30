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

    def build_payload_from_drf(self, detail, default_detail: str = "Dados inválidos.") -> dict:
        """
        Converte um ValidationError.detail (dict/list/str) do DRF no formato que o front espera:
          { ok: False, detail: "...", errors: { field: [ {message}, ... ] } }
        """
        def _to_list_of_msg(val):
            out = []
            if val is None:
                return out
            if isinstance(val, str):
                out.append({"message": val})
            elif isinstance(val, dict):
                # DRF às vezes traz {"message": "..."} ou {"detail": "..."}
                msg = val.get("message") or val.get("detail")
                if isinstance(msg, str):
                    out.append({"message": msg})
                else:
                    # flatten de subitens
                    for sub in val.values():
                        out += _to_list_of_msg(sub)
            elif isinstance(val, (list, tuple)):
                for item in val:
                    out += _to_list_of_msg(item)
            else:
                out.append({"message": str(val)})
            return out

        errors = {}

        if isinstance(detail, str):
            # Sem campos; manda como non_field_errors
            errors["non_field_errors"] = [{"message": detail}]
            return {"ok": False, "detail": detail or default_detail, "errors": errors}

        if isinstance(detail, (list, tuple)):
            # Lista de mensagens gerais
            msgs = _to_list_of_msg(detail)
            errors["non_field_errors"] = msgs or [{"message": default_detail}]
            text = "; ".join(m["message"] for m in msgs) if msgs else default_detail
            return {"ok": False, "detail": text, "errors": errors}

        if isinstance(detail, dict):
            # Dict por campo
            text_parts = []
            for field, val in detail.items():
                # DRF usa "non_field_errors" ou "__all__"
                key = "non_field_errors" if field in {"non_field_errors", "__all__"} else str(field)
                msgs = _to_list_of_msg(val)
                if msgs:
                    errors[key] = msgs
                    # para detail textual agregada
                    first = msgs[0]["message"]
                    text_parts.append(f"{key}: {first}" if key != "non_field_errors" else first)
            text = "; ".join(text_parts) if text_parts else default_detail
            return {"ok": False, "detail": text, "errors": errors}

        # fallback
        return {"ok": False, "detail": default_detail, "errors": {"non_field_errors": [{"message": default_detail}]}} 

    def raise_drf_validation_error(self, detail, default_detail: str = "Dados inválidos."):
        """
        Atalho para lançar no formato padronizado (se você quiser usar em algum ponto).
        """
        from rest_framework.exceptions import ValidationError
        payload = self.build_payload_from_drf(detail, default_detail=default_detail)
        raise ValidationError(payload)

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
