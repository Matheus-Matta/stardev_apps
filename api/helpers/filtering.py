# api/helpers/filtering.py
"""
Parser de filtros seguros vindos da querystring.
Suporta lookups básicos (exact, icontains, in, gt, gte, lt, lte, startswith, istartswith, endswith, iendswith).
Bloqueia travessia de relações (proíbe "__" no nome do campo, exceto para o sufixo de lookup).
Aceita order_by (-campo) e paginação (limit, offset).
Converte tipos simples (bool, int, float, uuid).
"""

from typing import Dict, Tuple, Set, Iterable, Any
from uuid import UUID
from django.db.models import Q, CharField, TextField, EmailField, SlugField
SEARCHABLE_FIELD_TYPES = (CharField, TextField, EmailField, SlugField)

ALLOWED_LOOKUPS: Set[str] = {
    "exact", "icontains", "in",
    "gt", "gte", "lt", "lte",
    "startswith", "istartswith",
    "endswith", "iendswith",
}

def _to_bool(v: str):
    s = (v or "").strip().lower()
    if s in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "f", "no", "n", "off"}:
        return False
    return v

def _coerce_value(raw: str) -> Any:
    b = _to_bool(raw)
    if isinstance(b, bool):
        return b
    try:
        return int(raw)
    except Exception:
        pass
    try:
        return float(raw)
    except Exception:
        pass
    try:
        return str(UUID(str(raw)))
    except Exception:
        pass
    return raw

def parse_list_query(params, allowed_fields: Iterable[str]) -> Tuple[Dict[str, Any], str, int, int]:
    """
    Recebe request.query_params e um iterável de campos permitidos (normalmente, os do ModelForm).
    Retorna: (filters, order_by, limit, offset)
    - filters: dict pronto para passar no .filter(**filters)
    - order_by: string vazia ou "campo" / "-campo"
    - limit/offset: ints (com saneamento)
    """
    allowed = set(allowed_fields or [])
    filters: Dict[str, Any] = {}

    order_by = (params.get("order_by") or "").strip()
    limit = params.get("limit", "100").strip()
    offset = params.get("offset", "0").strip()

    try:
        limit = max(1, min(1000, int(limit)))
    except Exception:
        limit = 100
    try:
        offset = max(0, int(offset))
    except Exception:
        offset = 0

    if order_by:
        raw = order_by.lstrip("-")
        if raw not in allowed:
            order_by = "" 

    for k, v in params.items():
        if k in {"order_by", "limit", "offset"}:
            continue
        if not v and v != "0":
            continue

        parts = k.split("__")
        if len(parts) == 1:
            field = parts[0]
            lookup = "exact"
        elif len(parts) == 2:
            field, lookup = parts
        else:
            continue

        if field not in allowed:
            continue

        if lookup not in ALLOWED_LOOKUPS:
            continue

        if lookup == "in":
            items = [s.strip() for s in str(v).split(",") if s.strip() != ""]
            filters[f"{field}__{lookup}"] = [_coerce_value(x) for x in items]
        else:
            filters[f"{field}__{lookup}"] = _coerce_value(v)

    return filters, order_by, limit, offset

def get_searchable_fields(model_cls, allowed_fields):
    """
    Retorna os nomes dos campos do model que:
      - estão no conjunto permitido (ex.: fields do ModelForm)
      - são de texto (Char/Text/Email/Slug)
    """
    out = []
    allowed = set(allowed_fields or [])
    for name in allowed:
        try:
            mf = model_cls._meta.get_field(name)
        except Exception:
            continue
        if isinstance(mf, SEARCHABLE_FIELD_TYPES):
            out.append(name)
    return out


def build_global_search_q(model_cls, allowed_fields, raw_search):
    """
    Monta um Q que faz OR em todos os campos pesquisáveis para cada termo,
    e AND entre os termos. Ex.: "foo bar" => (c1~foo OR c2~foo) AND (c1~bar OR c2~bar)
    """
    term = (raw_search or "").strip()
    if not term:
        return None

    fields = get_searchable_fields(model_cls, allowed_fields)
    if not fields:
        return None

    terms = [t for t in term.split() if t]
    if not terms:
        return None

    q = Q()
    for t in terms:
        sub = Q()
        for f in fields:
            sub |= Q(**{f + "__icontains": t})
        q &= sub
    return q

