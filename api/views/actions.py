from __future__ import annotations
from rest_framework import status
from rest_framework.response import Response
from .base import BaseModelView
from api.actions.registry import get_action, REGISTRY

class ActionView(BaseModelView):
    """
    POST /api/<model_name>/<action_name>/
    Body: deve ser um ARRAY. Ex.: [1,2,3] OU [{"id":1}, {"id":2}]
    """
    def post(self, request, model_name: str, action_name: str):
        print("action_name", action_name, request.data)
        helper = self.get_helper(request)
        model_cls = helper.resolve_model(model_name)
        if not model_cls:
            return self.not_found("Modelo inexistente.")

        action = get_action(model_cls.__name__, action_name)
        if not action:
            return self.not_found("Ação inexistente para este modelo.")

        perm_resp = self.exec_with_errors(
            action.check_perm, request, model_cls.__name__, obj=None, allow_self=False, allow_all=self.ALLOWED_PERMISSIONS
        )
        if isinstance(perm_resp, Response):
            return perm_resp

        qs = helper.get_queryset(model_cls.__name__)
        if qs is None:
            return self.fail("Queryset indisponível para o modelo.")

        account = getattr(request, "account", None)
        account_id = getattr(account, "id", None)
        account_field = helper.resolver.find_account_fk_field(model_cls)
        if account_field:
            if not account_id:
                return self.ok({"detail": "Sem tenant.", "processed": 0})
            qs = qs.filter(**{f"{account_field}_id": account_id})

        data = request.data
        if not isinstance(data, list):
            return self.fail("Payload inválido: envie um array.", http_status=status.HTTP_400_BAD_REQUEST)

        def _run():
            result = action.run(request, helper, model_cls, qs, data)
            if not result.ok:
                return self.fail(result.detail or "Falha na action.", http_status=result.http_status, extra=(result.payload or {}))
            return self.ok(
                {
                    "detail": result.detail or "Action executada com sucesso.",
                    "action": action.name,
                    "model": model_cls.__name__,
                    **(result.payload or {}),
                },
                http_status=result.http_status
            )
        return self.exec_with_errors(_run)

class ListActionsView(BaseModelView):
    """
    GET /api/<model_name>/actions/
    Retorna nomes (e metadados) de actions globais + específicas da model.
    """
    def get(self, request, model_name: str):
        model_name = model_name.strip()
        global_dict = REGISTRY.get("*", {})
        model_dict  = REGISTRY.get(model_name, {})
        print(global_dict, model_dict)
        def _to_meta(d):
            return [
                {
                    "name": a.name,
                    "http_methods": list(a.http_methods),
                    "required_method": a.required_method,
                    "scope": ("global" if a.models is None else "model"),
                }
                for a in d.values()
            ]

        all_names = sorted(set(list(global_dict.keys()) + list(model_dict.keys())))

        return Response(
            {
                "ok": True,
                "model": model_name,
                "actions": all_names,
                "meta": {
                    "global": _to_meta(global_dict),
                    "specific": _to_meta(model_dict),
                },
            },
            status=status.HTTP_200_OK,
        )
