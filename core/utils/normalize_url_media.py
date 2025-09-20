# utils/urls.py
from urllib.parse import urlparse
from django.conf import settings

def normalize_url_media(url: str | None) -> str | None:
    """
    Normaliza URL de mídia:
    - Se já começa com http:// ou https://, retorna como está.
    - Se for relativa (ex.: /media/...), prefixa com settings.BASE_URL.
    - Se None, retorna None.
    """
    if not url:
        return None

    parsed = urlparse(url)
    if parsed.scheme in ("http", "https"):
        return url

    base = getattr(settings, "BASE_URL", "").rstrip("/")
    if not base:
        return url  # fallback: devolve relativo

    if not url.startswith("/"):
        url = "/" + url
    return f"{base}{url}"
