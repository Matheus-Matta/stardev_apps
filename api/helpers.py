# api/helpers.py
from typing import Optional, Any, Type, Dict
from django.apps import apps as django_apps
from django.db.models import Model, QuerySet
from django.db.models import FileField, ImageField, ForeignKey, ManyToManyField
from django.forms import ModelForm
from django.forms import models as model_forms
from django.utils.module_loading import import_string
from datetime import date, datetime
from django.core.exceptions import PermissionDenied
from typing import Optional, Any, Type, Dict, Iterable
from rest_framework.exceptions import ValidationError 
from django.forms.models import model_to_dict
from core.utils.normalize_url_media import normalize_url_media
from django.db.models.fields.files import FieldFile

class ModelHelper:
    """
    Helper para:
      - resolver Model por nome
      - filtrar queryset por Account
      - serializar APENAS os campos definidos no ModelForm (fields)
    Uso:
        h = ModelHelper(request)
        obj = h.get_one("account.User", pk)
        data = h.serialize_using_form("account.User", obj)  # dict com só os campos do form
        # ou direto:
        data = h.get_one_serialized("User", pk)
    """

    def __init__(self, request):
        self.request = request
        self.account = getattr(request, "account", None)
        self.account_id: Optional[Any] = getattr(self.account, "id", None)

    def create_one(self, model_name: str, payload: Dict[str, Any]) -> Dict[str, Any] | None:
        try:
            model_cls = self._resolve_model(model_name)
            if not model_cls:
                raise PermissionDenied("Modelo inexistente.")

            account_field = self._find_account_fk_field(model_cls)

            if self._is_account_model(model_cls):
                raise PermissionDenied("Criação de Account não é permitida neste endpoint.")

            safe_payload = dict(payload or {})
            for k in ("Account", "account", account_field, f"{account_field}_id"):
                safe_payload.pop(k, None)

            FormClass = self._resolve_modelform_for_model(model_cls)
            instance = model_cls()

            if account_field:
                self._ensure_account_on_instance(instance, account_field)

            form = FormClass(
                data=safe_payload,
                files=getattr(self.request, "FILES", None),
                instance=instance,
            )
            if not form.is_valid():
                msg = self._errors_to_text(form)
                print("create_one form.errors:", dict(form.errors))
                raise ValidationError(msg)

            obj = form.save(commit=False)

            if account_field:
                self._ensure_account_on_instance(obj, account_field)

            obj.save()
            if hasattr(form, "save_m2m"):
                form.save_m2m()

            return self.serialize_using_form(model_name, obj)

        except Exception as e:
            print(f"[ModelHelper.create_one] Exception: {e!r} | model={model_name} | payload_keys={list((payload or {}).keys())}")
            raise
        
    def update_one(self, model_name: str, pk: Any, payload: Dict[str, Any]) -> Dict[str, Any] | None:
        try:
            obj = self.get_one(model_name, pk)
            if not obj:
                return None

            model_cls = obj.__class__
            account_field = self._find_account_fk_field(model_cls)

            safe_payload = dict(payload or {})
            for k in ("Account", "account", account_field, f"{account_field}_id"):
                safe_payload.pop(k, None)

            FormClass = self._resolve_modelform_for_model(model_cls)

            base_data = model_to_dict(obj)
            merged = {**base_data, **safe_payload}

            form = FormClass(
                data=merged,
                files=getattr(self.request, "FILES", None),
                instance=obj,
            )
            if not form.is_valid():
                msg = self._errors_to_text(form)
                print("update_one form.errors:", dict(form.errors))
                raise ValidationError(msg)

            updated = form.save(commit=False)

            if account_field:
                self._ensure_account_on_instance(updated, account_field)

            updated.save()
            if hasattr(form, "save_m2m"):
                form.save_m2m()

            return self.serialize_using_form(model_name, updated)

        except Exception as e:
            print(f"[ModelHelper.update_one] Exception: {e!r} | model={model_name} | pk={pk}")
            raise

    def delete_one(self, model_name: str, pk: Any) -> bool:
        try:
            obj = self.get_one(model_name, pk)
            if not obj:
                return False

            model_cls = obj.__class__
            user = getattr(self.request, "user", None)
            is_super = bool(getattr(user, "is_superuser", False))

            if self._is_account_model(model_cls) and not is_super:
                raise PermissionDenied("Sem permissão para deletar Account.")

            obj.delete()
            return True
        except PermissionDenied:
            raise
        except Exception as e:
            print(f"[ModelHelper.delete_one] Exception: {e!r} | model={model_name} | pk={pk}")
            raise

    def resolve_model(self, model_name: str) -> Optional[Type[Model]]:
        try:
            return self._resolve_model(model_name)
        except Exception as e:
            print(f"[ModelHelper.resolve_model] erro ao resolver model '{model_name}': {e!r}")
            raise

    def get_queryset(self, model_name: str) -> Optional[QuerySet]:
        try:
            model_cls = self._resolve_model(model_name)
            if not model_cls:
                return None

            user = getattr(self.request, "user", None)
            is_super = bool(getattr(user, "is_superuser", False))

            if self._is_account_model(model_cls):
                if is_super:
                    return model_cls.objects.all()
                if not self.account_id:
                    return None
                return model_cls.objects.filter(pk=self.account_id)

            account_field = self._find_account_fk_field(model_cls)
            if not account_field:
                return model_cls.objects.all() if is_super else None

            if is_super:
                return model_cls.objects.all()

            if not self.account_id:
                return None

            return model_cls.objects.filter(**{f"{account_field}_id": self.account_id})
        except Exception as e:
            print(f"[ModelHelper.get_queryset] erro ao montar queryset '{model_name}': {e!r}")
            raise

    def get_one(self, model_name: str, pk: Any) -> Optional[Model]:
        try:
            qs = self.get_queryset(model_name)
            if qs is None:
                return None
            return qs.filter(pk=pk).first() or None
        except Exception as e:
            print(f"ModelHelper.get_one: Exception resolving one for model {model_name} {pk}: {str(e)}")
            raise

    def get_one_serialized(self, model_name: str, pk: Any) -> Optional[Dict[str, Any]]:
        try:
            obj = self.get_one(model_name, pk)
            if not obj:
                return None
            return self.serialize_using_form(model_name, obj)
        except Exception as e:
            print(f"ModelHelper.get_one_serialized: Exception serializing one for model {model_name} with pk {pk} {str(e)}")
            raise


    def serialize_using_form(self, model_name: str, instance: Model) -> Optional[Dict[str, Any]]:
        try:
            model_cls = self._resolve_model(model_name)
            if not model_cls or not isinstance(instance, model_cls):
                return None

            FormClass = self._resolve_modelform_for_model(model_cls)
            form = FormClass(instance=instance)

            data: Dict[str, Any] = {
                "model": getattr(model_cls._meta, "label_lower", model_cls.__name__.lower()),
                "id": str(instance.pk),
                "fields": {},
            }

            for name, field in form.fields.items():
                value = getattr(instance, name, None)

                try:
                    model_field = model_cls._meta.get_field(name)
                except Exception:
                    model_field = None

                if value in (None, ""):
                    initial = getattr(field, "initial", None)
                    if initial not in (None, ""):
                        value = initial
                    else:
                        try:
                            bound = form[name]  # BoundField
                            bv = bound.value()
                            if bv not in (None, ""):
                                value = bv
                        except Exception:
                            pass

                if isinstance(model_field, ManyToManyField):
                    data["fields"][name] = list(getattr(instance, name).values_list("pk", flat=True))
                    continue

                if isinstance(model_field, ForeignKey):
                    data["fields"][name] = getattr(value, "pk", None)
                    continue

                if isinstance(model_field, (FileField, ImageField)):
                    ff: FieldFile = getattr(instance, name, None)
                    if isinstance(ff, FieldFile) and ff:
                        try:
                            url = normalize_url_media(getattr(ff, "url", None))
                        except Exception:
                            url = None
                        data["fields"][name] = {
                            "name": getattr(ff, "name", None),
                            "url": url,
                        }
                    else:
                        data["fields"][name] = None
                    continue

                if isinstance(value, (datetime, date)):
                    data["fields"][name] = value.isoformat()
                    continue

                data["fields"][name] = value

            return data
        except Exception as e:
            print(f"ModelHelper.serialize_using_form: Exception serializing instance of model {model_name} -> {e!r}")
            raise ValidationError(str(e))

    # ---------------- Internos ----------------
    
    def _is_account_model(self, model_cls) -> bool:
        """
        Detecta se o model é 'Account', independente do app label.
        """
        try:
            if model_cls.__name__.lower() == "account":
                return True
            return str(getattr(model_cls._meta, "label_lower", "")).endswith(".account")
        except Exception as e:
            print(f"ModelHelper._is_account_model: Exception checking if model is Account: {str(e)}")
            raise
        
    def _resolve_model(self, model_name: str) -> Optional[Type[Model]]:
        name = (model_name or "").strip()
        if not name:
            return None

        if "." in name:
            app_label, model = name.split(".", 1)
            return django_apps.get_model(app_label, model)

        name_lower = name.lower()
        for model in django_apps.get_models():
            if model.__name__.lower() == name_lower:
                return model
        return None

    def _find_account_fk_field(self, model_cls: Type[Model]) -> Optional[str]:
        for candidate in ("Account", "account", "tenant", "Tenant"):
            try:
                field = model_cls._meta.get_field(candidate)
                if isinstance(field, ForeignKey):
                    return field.name
            except Exception:
                pass

        try:
            AccountModel = (
                django_apps.get_model("core", "Account")
                or django_apps.get_model("account", "Account")
            )
        except Exception:
            AccountModel = None

        if AccountModel:
            for field in model_cls._meta.get_fields():
                if isinstance(field, ForeignKey) and getattr(field, "remote_field", None):
                    if field.remote_field.model is AccountModel:
                        return field.name
        return None

    def _resolve_modelform_for_model(self, model_cls) -> ModelForm:
        """
        Tenta <app>.forms.<ModelName>Form; senão, cria um ModelForm automático (fields='__all__').
        """
        app_label = model_cls._meta.app_label
        form_class_path = f"{app_label}.forms.{model_cls.__name__}Form"
        try:
            return import_string(form_class_path)
        except Exception as e:
            print(f"ModelHelper._resolve_modelform_for_model: Exception resolving modelform for model {model_cls} {str(e)}")
            return model_forms.modelform_factory(model=model_cls, fields="__all__")
        
    def _build_partial_form(
        self,
        model_cls: Type[Model],
        BaseFormClass: Type[ModelForm],
        instance: Model,
        payload: Dict[str, Any],
        is_super: bool,
        account_field: Optional[str],
    ) -> ModelForm:
        """
        Constrói um ModelForm **parcial**, limitado aos campos realmente enviados no payload.
        - ignora campos não pertencentes ao form base
        - remove 'Account' do conjunto (se não for superuser)
        """
        try:
            base_form = BaseFormClass(instance=instance)
            base_fields: Iterable[str] = list(base_form.fields.keys())

            allowed_names = [name for name in base_fields if name in payload]

            if not allowed_names:
                EmptyFormClass = model_forms.modelform_factory(model_cls, fields=[])
                return EmptyFormClass(data={}, instance=instance)

            if account_field and not is_super:
                allowed_names = [n for n in allowed_names if n not in {account_field, "Account", "account"}]

            PartialFormClass = model_forms.modelform_factory(model_cls, fields=allowed_names)

            form = PartialFormClass(data={k: payload[k] for k in allowed_names}, instance=instance)

            return form
        except Exception as e:
            print(f"[ModelHelper._build_partial_form] Exception building partial form: {e!r}")
            raise
        
    def _errors_to_text(self, form) -> str:
        """
        Converte form.errors em uma string única legível.
        Ex.: "image: Este campo é obrigatório.; label: Já existe com este valor."
        """
        try:
            parts = []
            for field, errors in form.errors.items():
                for err in errors:
                    parts.append(f"{field}: {err}")
            try:
                for err in form.non_field_errors():
                    parts.append(str(err))
            except Exception:
                pass
            return "; ".join(parts) if parts else "Dados inválidos."
        except Exception:
            return "Dados inválidos."

    def _ensure_account_on_instance(self, instance: Model, account_field: str):
        """
        Sempre força o tenant do request.account no instance.
        """
        if not self.account_id:
            raise PermissionDenied("Contexto de Account ausente em request.account.")
        setattr(instance, f"{account_field}_id", self.account_id)