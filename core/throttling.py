# core/throttling.py
from rest_framework.throttling import SimpleRateThrottle, ScopedRateThrottle

def get_account_slug(request):
    """
    Origem do 'account':
    - Se você já injeta request.account em um middleware, use isso.
    - Senão, tente o header 'X-Account-Slug'.
    """
    if hasattr(request, "account") and request.account:
        return getattr(request.account, "slug", None)
    return request.headers.get("X-Account-Slug") or request.META.get("HTTP_X_ACCOUNT_SLUG")


class AccountRateThrottle(SimpleRateThrottle):
    """
    Rate limit global por Account.
    Usa a taxa definida em DEFAULT_THROTTLE_RATES['account'].
    Bucket por 'acct:<slug>' (ou 'public' se não houver slug).
    """
    scope = "account"

    def get_cache_key(self, request, view):
        slug = get_account_slug(request)
        ident = f"acct:{slug}" if slug else "public"
        return self.cache_format % {"scope": self.scope, "ident": ident}


class AccountScopedRateThrottle(ScopedRateThrottle):
    """
    Igual ao ScopedRateThrottle, mas a chave inclui o Account.
    A 'rate' ainda vem de DEFAULT_THROTTLE_RATES[self.scope].
    """
    def get_cache_key(self, request, view):
        slug = get_account_slug(request) or "public"
        # self.scope vem da view (throttle_scope = "algum:escopo")
        ident = f"acct:{slug}:{self.scope}"
        return self.cache_format % {"scope": self.scope, "ident": ident}
