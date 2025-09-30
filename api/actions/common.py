from __future__ import annotations
from typing import Any, List
from django.db import transaction
from rest_framework import status
from .base import BaseAction, ActionResult
from .decorators import action_global

@action_global(name="bulk_delete", http_methods=("POST",), required_method="DELETE")
class BulkDeleteAction(BaseAction):
    """
    Recebe payload como array (obrigatório). Ex.: [1,2,3] ou ["uuid1","uuid2"]
    """
    def run(self, request, helper, model_cls, base_qs, items: List[Any]) -> ActionResult:
        ids = []
        for it in items:
            if isinstance(it, dict):
                it = it.get("id")
            if it is not None:
                ids.append(it)
        if not ids:
            return ActionResult(False, status.HTTP_400_BAD_REQUEST, detail="Envie uma lista de IDs no payload.")

        qs = base_qs.filter(id__in=ids).only("id")
        found_ids = set(qs.values_list("id", flat=True))
        not_found = [i for i in ids if i not in found_ids]

        with transaction.atomic():
            to_delete = list(found_ids)
            qs.delete()

        return ActionResult(
            ok=True,
            http_status=status.HTTP_200_OK,
            detail=f"{model_cls.__name__}: {len(to_delete)} item(ns) deletado(s).",
            payload={"deleted_ids": to_delete, "not_found": not_found},
        )
