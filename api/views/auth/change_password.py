from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from django.http import QueryDict
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser


class ChangePasswordView(APIView):
    """
    POST /auth/change-password
    Espera: { "current_password": "...", "new_password": "..." }
    Valida a senha atual do request.user e altera para a nova.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "user:1minute"
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def post(self, request, *args, **kwargs):
        data = request.data if isinstance(request.data, (dict, QueryDict)) else {}
        current_password = (data.get("currentPassword") or "").strip()
        new_password = (data.get("newPassword") or "").strip()

        if not current_password or not new_password:
            return Response(
                {"ok": False, "detail": "Campos 'current_password' e 'new_password' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        if not user.is_authenticated:
            return Response(
                {"ok": False, "detail": "Não autenticado."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(current_password):
            return Response(
                {"ok": False, "detail": "Senha atual inválida."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if current_password == new_password:
            return Response(
                {"ok": False, "detail": "A nova senha não pode ser igual à senha atual."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            password_validation.validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            return Response(
                {"data": {"ok": False, "errors": exc.messages}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response(
            {"ok": True, "detail": "Senha alterada com sucesso."},
            status=status.HTTP_200_OK,
        )
