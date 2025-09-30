from __future__ import annotations
from collections import defaultdict
from typing import Dict, Optional
from .base import BaseAction

REGISTRY: Dict[str, Dict[str, BaseAction]] = defaultdict(dict)

def register_action_instance(action: BaseAction) -> None:
    targets = action.models or ("*",)
    for target in targets:
        REGISTRY[target][action.name] = action

def get_action(model_name: str, action_name: str) -> Optional[BaseAction]:
    if model_name in REGISTRY and action_name in REGISTRY[model_name]:
        return REGISTRY[model_name][action_name]
    if "*" in REGISTRY and action_name in REGISTRY["*"]:
        return REGISTRY["*"][action_name]
    return None
