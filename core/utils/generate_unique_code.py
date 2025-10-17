# core/utils.py
from django.db import transaction

def generate_unique_code(instance, model_class, prefix='AA'):
    """
    Gera um código único no formato PREFIX-N dentro do escopo do Account.
    Ex.: BST-1, BST-2, ...

    Requisitos:
      - Modelo deve ter FK 'Account'
      - Campo de código chama-se 'code'
      - Unicidade (Account, code) garantida por constraint no DB
    """
    if not hasattr(instance, 'Account') or not instance.Account:
        raise ValueError("Instance must have a valid 'Account' attribute.")

    account = instance.Account
    base = f"{prefix}-"

    with transaction.atomic():
        try:
            current = model_class.objects.filter(Account=account).count()
        except Exception:
            current = 0

        n = max(1, current + 1)

        while True:
            code = f"{base}{n}"
            exists = (
                model_class.objects
                .filter(Account=account, code=code)
                .exclude(id=getattr(instance, 'id', None))
                .exists()
            )
            if not exists:
                return code
            n += 1
