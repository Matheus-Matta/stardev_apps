# account/signals.py
import os
import logging
from django.db import transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from core.models import Account, Business, BusinessType ,AccountModule, ModuleType

log = logging.getLogger(__name__)

def env(name: str, default: str = "") -> str:
    v = os.environ.get(name)
    return v if v is not None and v.strip() != "" else default

@receiver(post_migrate)
def seed_initial(sender, **kwargs):
    """
    Após migrações:
    - roda apenas quando o app 'account' é migrado
    - se não existir NENHUM Account, Business e User => cria os primeiros
    - idempotente (não recria se já existir qualquer registro)
    """
    try:
        # Se já existe qualquer dado, não faz nada
        if Account.objects.exists() or Business.objects.exists() or get_user_model().objects.exists():
            return

        # Variáveis de ambiente (ou defaults)
        ACC_SLUG = env("SEED_ACCOUNT_SLUG", "default")
        ACC_LEGAL = env("SEED_ACCOUNT_LEGAL_NAME", "Empresa Exemplo LTDA")
        ACC_DISPLAY = env("SEED_ACCOUNT_DISPLAY_NAME", "Empresa Exemplo")
        ACC_TZ = env("SEED_ACCOUNT_TZ", "America/Sao_Paulo")

        BIZ_CODE = env("SEED_BUSINESS_CODE", "HQ")
        BIZ_NAME = env("SEED_BUSINESS_NAME", "Matriz")
        BIZ_CNPJ = env("SEED_BUSINESS_CNPJ", "00.000.000/0000-00")  # ajuste depois para um válido
        BIZ_TYPE = env("SEED_BUSINESS_TYPE", BusinessType.COMPANY)    # 'company', 'store', ...

        ADMIN_USER = env("SEED_ADMIN_USERNAME", "admin")
        ADMIN_EMAIL = env("SEED_ADMIN_EMAIL", "admin@example.com")
        ADMIN_PASS = env("SEED_ADMIN_PASSWORD", "ChangeMe!123")  # mude em produção

        with transaction.atomic():
            # 1) Account
            account = Account.objects.create(
                slug=ACC_SLUG.lower(),
                legal_name=ACC_LEGAL,
                display_name=ACC_DISPLAY,
                time_zone=ACC_TZ,
                is_active=True,
            )

            # 2) Business (unidade vinculada)
            business = Business.objects.create(
                Account=account,
                code=BIZ_CODE,
                name=BIZ_NAME,
                cnpj=BIZ_CNPJ,
                business_type=BIZ_TYPE,
                is_active=True,
            )

            # 3) Módulos básicos habilitados para o Account
            # (ajuste conforme seu critério; aqui habilitamos todos como enabled)
            for mod in [ModuleType.ERP, ModuleType.TMS, ModuleType.PDV, ModuleType.WMS]:
                AccountModule.objects.create(
                    account=account,
                    module=mod,
                    features={},    # adicione flags conforme necessário
                    is_enabled=True,
                )

            # 4) Superuser vinculado ao Account
            User = get_user_model()
            # Garantir unicidade dentro do tenant
            if User.objects.filter(Account=account, username=ADMIN_USER).exists():
                # extremamente improvável já que user table está vazia; só por segurança
                ADMIN_USER = f"{ADMIN_USER}-{account.slug}"

            superuser = User.objects.create_superuser(
                username=ADMIN_USER,
                email=ADMIN_EMAIL,
                password=ADMIN_PASS,
                Account=account,
                display_name="Administrador",
                is_active=True,
            )

        log.warning(
            "Seed inicial criado: Account '%s', Business '%s', Superuser '%s' (altere a senha!)",
            account.slug, business.code, superuser.username
        )

    except Exception as exc:
        # Não interrompe o fluxo de migração, mas registra para você ver no console
        log.exception("Falha ao executar seed inicial do app 'account': %s", exc)
# account/signals.py
import os
import logging
from django.db import transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from core.models import Account, Business, BusinessType ,AccountModule, ModuleType

log = logging.getLogger(__name__)

def env(name: str, default: str = "") -> str:
    v = os.environ.get(name)
    return v if v is not None and v.strip() != "" else default

@receiver(post_migrate)
def seed_initial(sender, **kwargs):
    """
    Após migrações:
    - roda apenas quando o app 'account' é migrado
    - se não existir NENHUM Account, Business e User => cria os primeiros
    - idempotente (não recria se já existir qualquer registro)
    """
    try:
        # Se já existe qualquer dado, não faz nada
        if Account.objects.exists() or Business.objects.exists() or get_user_model().objects.exists():
            return

        # Variáveis de ambiente (ou defaults)
        ACC_SLUG = env("SEED_ACCOUNT_SLUG", "default")
        ACC_LEGAL = env("SEED_ACCOUNT_LEGAL_NAME", "Empresa Exemplo LTDA")
        ACC_DISPLAY = env("SEED_ACCOUNT_DISPLAY_NAME", "Empresa Exemplo")
        ACC_TZ = env("SEED_ACCOUNT_TZ", "America/Sao_Paulo")

        BIZ_CODE = env("SEED_BUSINESS_CODE", "HQ")
        BIZ_NAME = env("SEED_BUSINESS_NAME", "Matriz")
        BIZ_CNPJ = env("SEED_BUSINESS_CNPJ", "00.000.000/0000-00")  # ajuste depois para um válido
        BIZ_TYPE = env("SEED_BUSINESS_TYPE", BusinessType.COMPANY)    # 'company', 'store', ...

        ADMIN_USER = env("SEED_ADMIN_USERNAME", "admin")
        ADMIN_EMAIL = env("SEED_ADMIN_EMAIL", "admin@example.com")
        ADMIN_PASS = env("SEED_ADMIN_PASSWORD", "ChangeMe!123")  # mude em produção

        with transaction.atomic():
            # 1) Account
            account = Account.objects.create(
                slug=ACC_SLUG.lower(),
                legal_name=ACC_LEGAL,
                display_name=ACC_DISPLAY,
                time_zone=ACC_TZ,
                is_active=True,
            )

            # 2) Business (unidade vinculada)
            business = Business.objects.create(
                Account=account,
                code=BIZ_CODE,
                name=BIZ_NAME,
                cnpj=BIZ_CNPJ,
                business_type=BIZ_TYPE,
                is_active=True,
            )

            # 3) Módulos básicos habilitados para o Account
            # (ajuste conforme seu critério; aqui habilitamos todos como enabled)
            for mod in [ModuleType.ERP, ModuleType.TMS, ModuleType.PDV, ModuleType.WMS]:
                AccountModule.objects.create(
                    account=account,
                    module=mod,
                    features={},    # adicione flags conforme necessário
                    is_enabled=True,
                )

            # 4) Superuser vinculado ao Account
            User = get_user_model()
            # Garantir unicidade dentro do tenant
            if User.objects.filter(Account=account, username=ADMIN_USER).exists():
                # extremamente improvável já que user table está vazia; só por segurança
                ADMIN_USER = f"{ADMIN_USER}-{account.slug}"

            superuser = User.objects.create_superuser(
                username=ADMIN_USER,
                email=ADMIN_EMAIL,
                password=ADMIN_PASS,
                Account=account,
                display_name="Administrador",
                is_active=True,
            )

        log.warning(
            "Seed inicial criado: Account '%s', Business '%s', Superuser '%s' (altere a senha!)",
            account.slug, business.code, superuser.username
        )

    except Exception as exc:
        # Não interrompe o fluxo de migração, mas registra para você ver no console
        log.exception("Falha ao executar seed inicial do app 'account': %s", exc)
