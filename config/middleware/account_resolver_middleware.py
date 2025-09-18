# core/middleware.py
from __future__ import annotations

from django.utils.deprecation import MiddlewareMixin
from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework_simplejwt.backends import TokenBackend

def _get_account_model():
    """
    Tenta localizar o model Account de forma resiliente.
    Ajuste 'account.Account' abaixo se seu app/nome for diferente.
    """
    try:
        return django_apps.get_model("account", "Account")
    except Exception:
        try:
            return django_apps.get_model("core", "Account")
        except Exception:
            return None

def _extract_bearer_token(request) -> str | None:
    auth = request.META.get("HTTP_AUTHORIZATION") or request.headers.get("Authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None

def _decode_jwt(token: str) -> dict | None:
    """
    Decodifica o JWT sem tocar nas views do DRF.
    Respeita ALGORITHM/KEYS do SIMPLE_JWT.
    """
    try:
        cfg = getattr(settings, "SIMPLE_JWT", {})
        backend = TokenBackend(
            algorithm=cfg.get("ALGORITHM", "HS256"),
            signing_key=cfg.get("SIGNING_KEY", settings.SECRET_KEY),
            verifying_key=cfg.get("VERIFYING_KEY", None),
            audience=cfg.get("AUDIENCE", None),
            issuer=cfg.get("ISSUER", None),
            leeway=cfg.get("LEEWAY", 0),
        )
        return backend.decode(token, verify=True)
    except Exception:
        return None

def _get_user_account_from_user(user):
    """
    Tenta pegar o Account do usuário considerando campo 'account' OU 'Account'.
    """
    if not user:
        return None
    for attr in ("account", "Account"):
        if hasattr(user, attr):
            return getattr(user, attr, None)
    Account = _get_account_model()
    if Account is None:
        return None
    for fk_id_attr in ("account_id", "Account_id"):
        acc_id = getattr(user, fk_id_attr, None)
        if acc_id:
            try:
                return Account.objects.get(pk=acc_id, is_active=True)
            except Account.DoesNotExist:
                return None
    return None

class AccountResolverMiddleware(MiddlewareMixin):
    """
    Preenche request.account a partir de:
      1) Header X-Account-Slug
      2) request.user (se já autenticado por sessão)
      3) JWT Bearer (decodifica e busca o user → account)
    Seta também request.account_id.
    """

    def process_request(self, request):
        Account = _get_account_model()
        request.account = None
        request.account_id = None

        slug = request.headers.get("X-Account-Slug") or request.META.get("HTTP_X_ACCOUNT_SLUG")
        if slug and Account:
            try:
                acc = Account.objects.get(slug=str(slug).lower(), is_active=True)
                request.account = acc
                request.account_id = acc.pk
                return
            except Account.DoesNotExist:
                pass

        try:
            if getattr(request, "user", None) and request.user.is_authenticated:
                acc = _get_user_account_from_user(request.user)
                if acc:
                    request.account = acc
                    request.account_id = acc.pk
                    return
        except Exception:
            pass

        token = _extract_bearer_token(request)
        if token:
            payload = _decode_jwt(token)
            if payload:
                user_id_claim = getattr(settings, "SIMPLE_JWT", {}).get("USER_ID_CLAIM", "user_id")
                uid = payload.get(user_id_claim)
                if uid:
                    try:
                        User = get_user_model()
                        user = User.objects.filter(pk=uid).first()
                        acc = _get_user_account_from_user(user)
                        if acc:
                            request.account = acc
                            request.account_id = acc.pk
                            return
                    except Exception:
                        pass

        request.account = None
        request.account_id = None
