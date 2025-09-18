# core/export_mixin.py
from rest_framework import serializers

class ExportAwareSerializerMixin:
    """
    Remove, no __init__, campos declarados em EXPORT_EXCLUDE da própria model,
    exceto se o request.user for superuser/staff. Se não houver request ou user,
    aplica a exclusão (fail-safe).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        user_is_privileged = False
        if request and getattr(request, "user", None) and request.user.is_authenticated:
            user_is_privileged = bool(request.user.is_superuser or request.user.is_staff)

        # pega a model do serializer
        model = getattr(getattr(self, "Meta", None), "model", None)
        if not model:
            return  # nada pra fazer

        export_exclude = set(getattr(model, "EXPORT_EXCLUDE", []) or [])
        if not export_exclude:
            return

        # Se o usuário NÃO for privilegiado, remove os campos
        if not user_is_privileged:
            for field_name in list(self.fields.keys()):
                if field_name in export_exclude:
                    self.fields.pop(field_name)
