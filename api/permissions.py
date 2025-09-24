# api/permissions.py
from django.core.exceptions import PermissionDenied
from django.apps import apps as django_apps
from typing import Iterable

ACTIONS = {
    "GET": "view",
    "POST": "add",
    "PUT": "change",
    "PATCH": "change",
    "DELETE": "delete",
}

def resolve_model(model_name: str):
    model_name = (model_name or "").strip()
    if not model_name:
        return None
    if "." in model_name:
        app_label, name = model_name.split(".", 1)
        return django_apps.get_model(app_label, name)
    name_lower = model_name.lower()
    for model in django_apps.get_models():
        if model.__name__.lower() == name_lower:
            return model
    return None

def build_perm_codename(model_cls, action: str) -> str:
    """Retorna 'app_label.action_modelname', ex.: 'core.view_user'."""
    app_label = model_cls._meta.app_label
    model = model_cls._meta.model_name
    return f"{app_label}.{action}_{model}"

def allow_self_user_exception(user, model_cls, action: str, obj) -> bool:
    """Exceção: o usuário pode 'view' e 'change' o PRÓPRIO User."""
    if model_cls._meta.model_name == "user" and obj is not None:
        if action in ("view", "change") and str(obj.pk) == str(getattr(user, "pk", "")):
            return True
    return False

def require_model_permission(
    request,
    model_name: str,
    http_method: str,
    obj=None,
    *,
    allow_self: bool = False,
    allow_all: Iterable[str] = (),
):
    """
    Verifica permissão pelo método HTTP.

    Regras:
      - Se o usuário possuir QUALQUER perm em `allow_all`, libera sem checar o resto.
      - Caso contrário, aplica:
          - Exceção opcional `allow_self` (p/ o próprio User em view/change)
          - Checagem de perm 'app_label.<action>_<model>'

    Exemplo:
        require_model_permission(
            request, "core.User", "PUT", obj=user_obj,
            allow_self=True,
            allow_all=("core.change_files", "core.add_files")
        )
    """
    
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        raise PermissionDenied("Usuário não autenticado.")
     
    action = ACTIONS.get(str(http_method).upper())
    if not action:
        raise PermissionDenied("Ação não suportada para permissão.")

    model_cls = resolve_model(model_name)
    if not model_cls:
        raise PermissionDenied("Modelo inválido.")
    
    perm = build_perm_codename(model_cls, action)
    
    for perm in allow_all:
        return
        
    if allow_self and allow_self_user_exception(user, model_cls, action, obj):
        return

    if not user.has_perm(perm):
        raise PermissionDenied(f"Permissão negada: é necessário '{perm}'.")
