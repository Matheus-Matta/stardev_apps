from __future__ import annotations
from typing import Tuple, Optional
from .base import BaseAction
from .registry import register_action_instance

def action_global(
    *,
    name: str,
    http_methods: Tuple[str, ...] = ("POST",),
    required_method: str = "POST",
):
    """
    Decorator para registrar uma action GLOBAL (todas as models).
    """
    def _decorator(cls: type[BaseAction]):
        inst = cls()
        inst.name = name
        inst.models = None
        inst.http_methods = tuple(m.upper() for m in http_methods)
        inst.required_method = required_method.upper()
        register_action_instance(inst)
        return cls
    return _decorator

def action_for_models(
    *models: str,
    name: str,
    http_methods: Tuple[str, ...] = ("POST",),
    required_method: str = "POST",
):
    """
    Decorator para registrar uma action específica para uma ou mais models.
    Ex.: @action_for_models("Pedido", name="marcar_pagos", required_method="PUT")
    """
    def _decorator(cls: type[BaseAction]):
        inst = cls()
        inst.name = name
        inst.models = tuple(models)
        inst.http_methods = tuple(m.upper() for m in http_methods)
        inst.required_method = required_method.upper()
        register_action_instance(inst)
        return cls
    return _decorator
