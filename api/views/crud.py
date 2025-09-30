# api/views/crud.py
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime, time
from django.utils import timezone
from django.core.exceptions import FieldDoesNotExist

from .base import BaseModelView
from api.helpers.filtering import parse_list_query, build_global_search_q

class GetView(BaseModelView):
    def get(self, request, model_name: str, pk: str) -> Response:
        helper = self.get_helper(request)

        obj = helper.get_one(model_name, pk)
        if not obj:
            return self.not_found(f"{model_name} não encontrado")

        perm_resp = self.exec_with_errors(self.check_perm, request, model_name, "GET", obj=obj, allow_self=True)
        if isinstance(perm_resp, Response):
            return perm_resp

        def _run():
            serialized = helper.serialize_instance(model_name, obj)  # << trocado
            payload = self.wrap_serialized(serialized, model_name, pk)
            return self.ok(payload)

        return self.exec_with_errors(_run)

class PostView(BaseModelView):
    ALLOWED_PERMISSIONS = ("core.change_files", "core.add_files")

    def post(self, request, model_name: str) -> Response:
        perm_resp = self.exec_with_errors(self.check_perm, request, model_name, "POST", obj=None, allow_self=False)
        if isinstance(perm_resp, Response):
            return perm_resp

        helper = self.get_helper(request)
        payload = self.extract_payload(request)

        def _run():
            data = helper.create_one(model_name, payload)
            if data is None:
                return self.fail("Não foi possível criar.")
            wrapped = self.wrap_serialized(data, model_name)
            return self.created(model_name, wrapped)

        return self.exec_with_errors(_run)

class PutView(BaseModelView):
    ALLOWED_PERMISSIONS = ("core.change_files", "core.add_files")

    def put(self, request, model_name: str, pk: str) -> Response:
        helper = self.get_helper(request)

        obj = helper.get_one(model_name, pk)
        if not obj:
            return self.not_found()

        perm_resp = self.exec_with_errors(self.check_perm, request, model_name, "PUT", obj=obj, allow_self=True)
        if isinstance(perm_resp, Response):
            return perm_resp

        payload = self.extract_payload(request)

        def _run():
            data = helper.update_one(model_name, pk, payload)
            if data is None:
                return self.not_found()
            wrapped = self.wrap_serialized(data, model_name, pk)
            return self.updated(model_name, wrapped)

        return self.exec_with_errors(_run)

class DeleteView(BaseModelView):
    def delete(self, request, model_name: str, pk: str) -> Response:
        helper = self.get_helper(request)
        obj = helper.get_one(model_name, pk)
        if not obj:
            return self.not_found()

        perm_resp = self.exec_with_errors(self.check_perm, request, model_name, "DELETE", obj=obj, allow_self=False)
        if isinstance(perm_resp, Response):
            return perm_resp

        def _run():
            ok = helper.delete_one(model_name, pk)
            if not ok:
                return self.not_found()
            return self.deleted_ok(model_name)

        return self.exec_with_errors(_run)

class ListView(BaseModelView):
    def _plural_to_model(self, model_name_plural: str) -> str:
        name = (model_name_plural or "").strip().lower()
        if not name:
            return ""
        if name.endswith("ies"):
            singular = name[:-3] + "y"
        elif name.endswith("ses"):
            singular = name[:-2]
        elif name.endswith("es"):
            singular = name[:-2]
        elif name.endswith("s"):
            singular = name[:-1]
        else:
            singular = name
        return singular[:1].upper() + singular[1:]

    def get(self, request, model_name_plural: str) -> Response:
        helper = self.get_helper(request)
        model_name = self._plural_to_model(model_name_plural)

        model_cls = helper.resolve_model(model_name)
        if not model_cls:
            return self.not_found("Modelo inexistente.")

        perm_resp = self.exec_with_errors(
            self.check_perm, request, model_cls.__name__, "GET", obj=None, allow_self=False
        )
        if isinstance(perm_resp, Response):
            return perm_resp
        
        qs = helper.get_queryset(model_cls.__name__)
        if qs is None:
            return self.ok({model_name_plural: [], "count": 0})
        
        # reforço: se tiver tenant_fk, filtre de novo por segurança       
        account = getattr(request, "account", None)
        account_id = getattr(account, "id", None)
        account_field = helper.resolver.find_account_fk_field(model_cls)
        if account_field:
            if not account_id:
                return self.ok({model_name_plural: [], "count": 0})
            qs = qs.filter(**{f"{account_field}_id": account_id})
    
        allowed_fields = helper.get_serializer_fields(model_cls) or []
        if "id" not in allowed_fields:
            allowed_fields.append("id")

        def _parse_iso(dt_str: str) -> datetime | None:
            s = (dt_str or "").strip()
            if not s:
                return None
            try:
                return datetime.fromisoformat(s)
            except Exception:
                return None

        def _ensure_aware(dt: datetime) -> datetime:
            if timezone.is_naive(dt) and timezone.is_aware(timezone.now()):
                try:
                    return timezone.make_aware(dt, timezone.get_current_timezone())
                except Exception:
                    return timezone.make_aware(dt, timezone.utc)
            return dt

        start_raw = request.query_params.get("start_date") or request.query_params.get("start")
        end_raw   = request.query_params.get("end_date")   or request.query_params.get("end")

        start_dt = _parse_iso(start_raw)
        end_dt   = _parse_iso(end_raw)

        if end_dt and end_dt.time() == time(0, 0, 0) and end_raw and len(end_raw) == 10:
            end_dt = datetime.combine(end_dt.date(), time(23, 59, 59, 999999))

        if start_dt:
            start_dt = _ensure_aware(start_dt)
        if end_dt:
            end_dt = _ensure_aware(end_dt)

        try:
            model_cls._meta.get_field("created_at")
            if start_dt and end_dt:
                qs = qs.filter(created_at__range=(start_dt, end_dt))
            elif start_dt:
                qs = qs.filter(created_at__gte=start_dt)
            elif end_dt:
                qs = qs.filter(created_at__lte=end_dt)
        except FieldDoesNotExist:
            pass

        raw_search = request.query_params.get("search", "")
        q_search = build_global_search_q(model_cls, allowed_fields, raw_search)
        if q_search is not None:
            qs = qs.filter(q_search)

        filters, order_by, limit, offset = parse_list_query(request.query_params, allowed_fields)
        if filters:
            qs = qs.filter(**filters)
        if order_by:
            qs = qs.order_by(order_by)

        total = qs.count()
        page = list(qs[offset: offset + limit])

        rows = []
        for obj in page:
            data = helper.serialize_instance(model_cls.__name__, obj)  # << trocado
            rows.append({**(data.get("fields", {})), "id": data.get("id")})
        return self.ok({model_name_plural: rows, "count": total})
