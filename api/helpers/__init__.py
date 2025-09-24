# api/helpers/__init__.py
"""
Fachada pública compatível: ModelHelper.

Mantém a mesma interface que você já usa nas views (create_one/update_one/etc),
mas internamente delega para ModelService e classes especializadas.
"""

from .service import ModelService


class ModelHelper:
    """
    Fachada simples para manipular modelos com multi-tenant, validação e serialização.

    Uso:
        h = ModelHelper(request)
        obj = h.get_one("account.User", pk)
        data = h.serialize_using_form("account.User", obj)
    """

    def __init__(self, request):
        """Armazena a request e instancia o serviço interno."""
        self._service = ModelService(request)

    # API pública (compatível com a versão anterior)
    def create_one(self, model_name, payload):
        """Cria um registro do model informado com validações e tenant forçado."""
        return self._service.create_one(model_name, payload)

    def update_one(self, model_name, pk, payload):
        """Atualiza um registro com validação, tenant forçado e detecção de UNIQUE."""
        return self._service.update_one(model_name, pk, payload)

    def delete_one(self, model_name, pk):
        """Remove um registro de forma segura, respeitando as regras de tenant."""
        return self._service.delete_one(model_name, pk)

    def resolve_model(self, model_name):
        """Resolve dinamicamente uma classe de Model pelo nome (com ou sem app_label)."""
        return self._service.resolver.resolve_model(model_name)

    def get_queryset(self, model_name):
        """Retorna o queryset já filtrado pelo tenant/escopo do request."""
        return self._service.get_queryset(model_name)

    def get_one(self, model_name, pk):
        """Retorna uma instância filtrada pelo escopo do tenant, se existir."""
        return self._service.get_one(model_name, pk)

    def get_one_serialized(self, model_name, pk):
        """Retorna a instância serializada com base no ModelForm associado."""
        return self._service.get_one_serialized(model_name, pk)

    def serialize_using_form(self, model_name, instance):
        """Serializa uma instância usando os fields definidos no ModelForm do model."""
        return self._service.serializer.serialize_using_form(model_name, instance)
    
    def _resolve_modelform_for_model(self, model_name: str):
        try:
            return self._service.resolver.resolve_form_for_model(model_name)
        except Exception as e:
            print(f"[ModelHelper.resolve_model] erro ao resolver model '{model_name}': {e!r}")
            raise