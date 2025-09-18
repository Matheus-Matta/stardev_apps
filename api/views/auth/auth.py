# auth/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle

from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.http import QueryDict
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django.contrib.auth import get_user_model

from core.serialize import serialize_model

class LoginView(TokenObtainPairView):
    """
    Espera: { "email": "...", "password": "..." }
    Retorna: { "data": { "user": {...}, "tokens": {...} } }
    """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth:login"
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            if data is None or not isinstance(data, (dict, QueryDict)):
                data = {}

            email = (data.get("email") or "").strip()
            password = data.get("password")
            if not email or not password:
                return Response(
                    {"data": {"ok": False, "detail": "Campos 'email' e 'password' são obrigatórios."}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            User = get_user_model()
            user = User.objects.filter(email__iexact=email).first()
            if not user or not user.is_active or not user.check_password(password):
                return Response(
                    {"data": {"ok": False, "detail": "Credenciais inválidas."}},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            username_field = getattr(user, "USERNAME_FIELD", "username")
            ser = TokenObtainPairSerializer(data={
                "username": getattr(user, username_field, None) or getattr(user, "username", ""),
                "password": password,
            })
            
            ser.is_valid(raise_exception=True)
            tokens = ser.validated_data

            user_data = serialize_model(user, request=request)

            return Response({"data": {"user": user_data, "tokens": tokens}}, status=status.HTTP_200_OK)

        except ValidationError as exc:
            detail = exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail}
            return Response({"data": {"ok": False, **detail}}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print("LoginView error:", repr(e))
            return Response(
                {"data": {"ok": False, "detail": "Erro ao autenticar."}},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """
    Espera: { "refresh": "<refresh_token>" }
    Coloca o refresh em blacklist.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"data": {"ok": False, "detail": "Campo 'refresh' é obrigatório."}},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh)
            token.blacklist()
            return Response({"data": {"ok": True}}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(
                {"data": {"ok": False, "detail": "Refresh token inválido."}},
                status=status.HTTP_400_BAD_REQUEST
            )


class VerifyView(TokenVerifyView):
    """
    Espera: { "token": "<access_ou_refresh>" }
    Retorna: { "data": {"valid": true|false} }
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            s = self.get_serializer(data=request.data)
            s.is_valid(raise_exception=True)
            return Response({"data": {"valid": True}}, status=status.HTTP_200_OK)
        except ValidationError as exc:
            detail = exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail}
            return Response({"data": {"valid": False, **detail}}),
