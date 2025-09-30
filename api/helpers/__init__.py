# api/helpers/__init__.py
from .service import ModelService
from .resolver import ModelResolver

class ModelHelper:
    def __init__(self, request):
        self.service = ModelService(request)
        self.resolver = self.service.resolver

    def resolve_model(self, model_name: str):
        return self.resolver.resolve_model(model_name)

    def get_queryset(self, model_name: str):
        return self.service.get_queryset(model_name)

    def get_one(self, model_name: str, pk):
        return self.service.get_one(model_name, pk)

    def create_one(self, model_name: str, payload: dict):
        return self.service.create_one(model_name, payload)

    def update_one(self, model_name: str, pk, payload: dict):
        return self.service.update_one(model_name, pk, payload)

    def delete_one(self, model_name: str, pk):
        return self.service.delete_one(model_name, pk)

    def serialize_instance(self, model_name: str, instance):
        return self.service.serialize_instance(model_name, instance)

    def get_serializer_fields(self, model_cls) -> list[str]:
        return self.service.get_serializer_fields(model_cls)
