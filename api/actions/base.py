from __future__ import annotations
from typing import Any, Dict, Iterable, Optional, Protocol, Tuple
from dataclasses import dataclass
from django.db.models import Model, QuerySet
from api.permissions import require_model_permission

@dataclass
class ActionResult:
    ok: bool
    http_status: int = 200
    detail: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

class BaseAction:
    """
    Classe base para todas as actions.
    Defina nas subclasses:
      - name: str
      - http_methods: Tuple[str, ...] (ex.: ("POST",))
      - required_method: str         (método usado para checagem de permissão: GET/POST/PUT/PATCH/DELETE)
      - models: Tuple[str, ...] | None  (None => global, vale para todas)
    E implemente:
      - run(self, request, helper, model_cls, base_qs, items) -> ActionResult
    """
    name: str = ""
    http_methods: Tuple[str, ...] = ("POST",)
    required_method: str = "POST"
    models: Optional[Tuple[str, ...]] = None 

    def check_perm(
        self,
        request,
        model_name: str,
        *,
        obj=None,
        allow_self: bool = False,
        allow_all: Iterable[str] = (),
    ) -> None:
        require_model_permission(
            request,
            model_name,
            self.required_method,
            obj=obj,
            allow_self=allow_self,
            allow_all=allow_all,
        )

    def run(
        self,
        request,
        helper,
        model_cls: type[Model],
        base_qs: QuerySet,
        items: list[Any],
    ) -> ActionResult:
        raise NotImplementedError("Implemente em subclasses.")
