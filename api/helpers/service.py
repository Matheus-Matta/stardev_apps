# api/helpers/service.py
from typing import Optional, Any, Dict
from django.db.models import Model, QuerySet
from rest_framework.exceptions import ValidationError
from .resolver import ModelResolver
from .tenancy import AccountScope
from .errors import ErrorBuilder, UniqueErrorParser
from .drf_adapter import DRFSerializerAdapter

class ModelService:
    def __init__(self, request):
        self.request = request
        self.resolver = ModelResolver()
        self.scope = AccountScope(request, self.resolver)
        self.errors = ErrorBuilder()
        self.unique = UniqueErrorParser()
        self.serializer = DRFSerializerAdapter(self.resolver)

    def get_queryset(self, model_name: str) -> Optional[QuerySet]:
        model_cls = self.resolver.resolve_model(model_name)
        if not model_cls:
            return None
        return self.scope.get_queryset(model_cls)

    def get_one(self, model_name: str, pk: Any) -> Optional[Model]:
        qs = self.get_queryset(model_name)
        if qs is None:
            return None
        return qs.filter(pk=pk).first() or None

    def serialize_instance(self, model_name, instance):
        return self.serializer.serialize_instance(model_name, instance)

    def create_one(self, model_name, payload):
        obj = self.serializer.create(model_name, payload, context={"request": self.request})
        return self.serializer.serialize_instance(model_name, obj)

    def update_one(self, model_name, pk, payload):
        instance = self.get_one(model_name, pk)
        if not instance:
            return None
        obj = self.serializer.update(
            model_name,
            instance,
            payload,
            context={"request": self.request},
            partial=True,  
        )
        return self.serializer.serialize_instance(model_name, obj)

    def delete_one(self, model_name: str, pk: Any) -> bool:
        model_cls = self.resolver.resolve_model(model_name)
        if not model_cls:
            return False
        qs = self.scope.get_queryset(model_cls)
        if qs is None:
            return False
        obj = qs.filter(pk=pk).first()
        if not obj:
            return False
        obj.delete()
        return True

    def get_serializer_fields(self, model_cls):
        return self.serializer.get_serializer_fields(model_cls)
