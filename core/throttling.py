# core/throttling.py
from rest_framework.throttling import SimpleRateThrottle, ScopedRateThrottle
from rest_framework.exceptions import Throttled

def get_account_slug(request):
    """
    De onde vem o 'account'?
    - Se você já injeta request.account em um middleware, use isso.
    - Senão, tente por header 'X-Account-Slug'.
    """
    if hasattr(request, "account") and request.account:
        return getattr(request.account, "slug", None)
    return request.headers.get("X-Account-Slug") or request.META.get("HTTP_X_ACCOUNT_SLUG")

class AccountRateThrottle(SimpleRateThrottle):
    """
    Rate limit global por Account.
    Usa a taxa definida em DEFAULT_THROTTLE_RATES['account'].
    """
    scope = "account"

    def get_cache_key(self, request, view):
        slug = get_account_slug(request)
        if not slug:
            # Sem slug => opcional: negar ou cair num bucket 'public'
            # return None  # sem chave => sem throttling
            return self.cache_format % {"scope": self.scope, "ident": "public"}
        ident = f"acct:{slug}"
        return self.cache_format % {"scope": self.scope, "ident": ident}

class AccountScopedRateThrottle(ScopedRateThrottle):
    """
    Igual ao ScopedRateThrottle, mas com chave por Account + scope.
    Permite ter escopos diferentes por rota, todos por account.
    """
    def get_cache_key(self, request, view):
        slug = get_account_slug(request) or "public"
        # self.scope vem da view (throttle_scope)
        ident = f"acct:{slug}:{self.scope}"
        return self.cache_format % {"scope": self.scope, "ident": ident}
# core/throttling.py
from rest_framework.throttling import SimpleRateThrottle, ScopedRateThrottle
from rest_framework.exceptions import Throttled

def get_account_slug(request):
    """
    De onde vem o 'account'?
    - Se você já injeta request.account em um middleware, use isso.
    - Senão, tente por header 'X-Account-Slug'.
    """
    if hasattr(request, "account") and request.account:
        return getattr(request.account, "slug", None)
    return request.headers.get("X-Account-Slug") or request.META.get("HTTP_X_ACCOUNT_SLUG")

class AccountRateThrottle(SimpleRateThrottle):
    """
    Rate limit global por Account.
    Usa a taxa definida em DEFAULT_THROTTLE_RATES['account'].
    """
    scope = "account"

    def get_cache_key(self, request, view):
        slug = get_account_slug(request)
        if not slug:
            # Sem slug => opcional: negar ou cair num bucket 'public'
            # return None  # sem chave => sem throttling
            return self.cache_format % {"scope": self.scope, "ident": "public"}
        ident = f"acct:{slug}"
        return self.cache_format % {"scope": self.scope, "ident": ident}

class AccountScopedRateThrottle(ScopedRateThrottle):
    """
    Igual ao ScopedRateThrottle, mas com chave por Account + scope.
    Permite ter escopos diferentes por rota, todos por account.
    """
    def get_cache_key(self, request, view):
        slug = get_account_slug(request) or "public"
        # self.scope vem da view (throttle_scope)
        ident = f"acct:{slug}:{self.scope}"
        return self.cache_format % {"scope": self.scope, "ident": ident}
