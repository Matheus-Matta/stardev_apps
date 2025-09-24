# api/views/base.py
"""
Infraestrutura base para as views de modelo:
- Autenticação, throttling, parsers
- Padronização de respostas de sucesso
- Tratamento uniforme de erros (PermissionDenied, ValidationError, Exception)
- Checagem de permissão por operação (GET/POST/PUT/DELETE)
"""

from typing import Optional, Dict, Any
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.exceptions import ValidationError
from django.core.exceptions import PermissionDenied

from api.helpers import ModelHelper
from api.permissions import require_model_permission
from core.throttling import AccountScopedRateThrottle


class BaseModelView(APIView):
    """
    View base com:
      - auth/throttle/parser
      - criação do ModelHelper (fachada)
      - métodos utilitários de respostas e erro
      - checagem de permissão por método HTTP
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [AccountScopedRateThrottle]
    throttle_scope = "account:1hour"
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    ALLOWED_PERMISSIONS: tuple[str, ...] = ()

    def get_helper(self, request) -> ModelHelper:
        """Instancia e retorna um ModelHelper para a request atual."""
        return ModelHelper(request)

    def ok(self, data: Dict[str, Any], http_status: int = status.HTTP_200_OK) -> Response:
        """Retorna uma resposta de sucesso com `ok=True`."""
        return Response({"ok": True, **(data or {})}, status=http_status)

    def fail(self, detail: str, http_status: int = status.HTTP_400_BAD_REQUEST, extra: Optional[Dict[str, Any]] = None) -> Response:
        """Retorna uma resposta de falha com `ok=False`."""
        payload = {"ok": False, "detail": detail}
        if extra:
            payload.update(extra)
        return Response(payload, status=http_status)

    def not_found(self, detail: str = "Não encontrado") -> Response:
        """404 com payload padronizado."""
        return self.fail(detail, http_status=status.HTTP_404_NOT_FOUND)

    def forbidden(self, detail: str) -> Response:
        """403 com payload padronizado."""
        return self.fail(detail, http_status=status.HTTP_403_FORBIDDEN)

    def created(self, model_name: str, data: Dict[str, Any]) -> Response:
        """201 com payload de criação padronizado."""
        return self.ok(
            {"detail": f"{model_name} criado com sucesso!", **data},
            http_status=status.HTTP_201_CREATED,
        )

    def updated(self, model_name: str, data: Dict[str, Any]) -> Response:
        """200 com payload de atualização padronizado."""
        return self.ok({"detail": f"{model_name} atualizado com sucesso!", **data})

    def deleted_ok(self, model_name: str) -> Response:
        """200 com payload de deleção padronizado."""
        return self.ok({"detail": f"{model_name} deletado com sucesso!", "deleted": True})

    def extract_payload(self, request) -> Dict[str, Any]:
        """Extrai o payload do request.data."""
        return request.data if isinstance(request.data, dict) else {}

    def wrap_serialized(self, serialized: Dict[str, Any], model_name: str, pk: Optional[str] = None) -> Dict[str, Any]:
        """
        Recebe o dicionário vindo do FormSerializer:
          { model, id, fields: {...} }
        e converte para: { <model_name>: { id, <fields...> } }
        """
        fields = (serialized or {}).get("fields", {}) or {}
        fields["id"] = serialized.get("id") or pk or ""
        return {model_name: fields}

    def check_perm(self, request, model_name: str, http_method: str, *, obj=None, allow_self: bool = True) -> None:
        """
        Checa permissão do usuário para a operação.
        Lança PermissionDenied quando não autorizado.
        """
        require_model_permission(
            request,
            model_name,
            http_method.upper(),
            obj=obj,
            allow_self=allow_self,
            allow_all=self.ALLOWED_PERMISSIONS or (),
        )

    def exec_with_errors(self, fn, *args, **kwargs) -> Response | Any:
        """
        Executa uma função do fluxo principal e converte exceções em respostas DRF.
        - ValidationError: retorna exatamente o payload (dict) ou detail/400
        - PermissionDenied: 403
        - Exception: 400 genérico com 'errors'
        """
        try:
            return fn(*args, **kwargs)
        except PermissionDenied as e:
            return self.forbidden(str(e))
        except ValidationError as e:
            detail = getattr(e, "detail", str(e))
            if isinstance(detail, dict):
                return Response(detail, status=status.HTTP_400_BAD_REQUEST)
            return self.fail(str(detail))
        except Exception as e:
            # fallback: mantém compatibilidade com seu formato
            return self.fail("Erro ao processar a requisição.", extra={"errors": str(e)})
