# account/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

# ✅ IMPORTANTE: habilita o histórico no Admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Account,
    AccountModule,
    Business,
    BusinessType,
    User,
    Customer,
    CustomerAddress,
    CustomerContact,
    Address,
    Contact,
    ContactType,
    Files,
)


def _is_uuid(s: str) -> bool:
    from uuid import UUID

    try:
        UUID(s)
        return True
    except Exception:
        return False


# ------------------- Account -------------------
@admin.register(Account)
class AccountAdmin(SimpleHistoryAdmin):  # ⬅️ agora com histórico
    list_display = ("display_name", "slug", "is_active", "time_zone", "created_at")
    search_fields = ("slug", "display_name", "legal_name")
    list_filter = ("is_active",)
    ordering = ("slug",)


# ------------------- BusinessType -------------------
@admin.register(BusinessType)
class BusinessTypeAdmin(SimpleHistoryAdmin):  # ⬅️ histórico
    list_display = ("code", "name", "Account", "is_active", "created_at")
    search_fields = ("code", "name", "Account__slug", "Account__display_name")
    list_filter = ("is_active", "Account")
    ordering = ("Account__slug", "code")
    autocomplete_fields = ("Account",)
    readonly_fields = ("created_at", "updated_at")
    fields = ("Account", "code", "name", "is_active", "created_at", "updated_at")

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        acc = request.GET.get("Account") or request.GET.get("account")
        if acc and not _is_uuid(acc):
            try:
                initial["Account"] = str(Account.objects.only("id").get(slug=acc).pk)
            except Account.DoesNotExist:
                pass
        return initial


@admin.register(Business)
class BusinessAdmin(
    SimplyHistoryAdmin := SimpleHistoryAdmin
):  # ⬅️ histórico (py trick p/ reuso se quiser)
    list_display = ("code", "name", "cnpj", "Account", "business_type", "is_active")
    search_fields = (
        "code",
        "name",
        "cnpj",
        "Account__slug",
        "Account__display_name",
        "business_type__code",
        "business_type__name",
    )
    list_filter = ("business_type", "is_active", "Account")
    ordering = ("Account__slug", "code")
    autocomplete_fields = ("Account", "address", "parent", "business_type")
    readonly_fields = ("created_at", "updated_at")
    fields = (
        "Account",
        "code",
        "name",
        "cnpj",
        "business_type",
        "address",
        "parent",
        "is_active",
        "created_at",
        "updated_at",
    )

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        acc = request.GET.get("Account") or request.GET.get("account")
        if acc and not _is_uuid(acc):
            try:
                initial["Account"] = str(Account.objects.only("id").get(slug=acc).pk)
            except Account.DoesNotExist:
                pass
        return initial


# ------------------- User -------------------
@admin.register(User)
class UserAdmin(
    SimpleHistoryAdmin, BaseUserAdmin
):  # ⬅️ SimpleHistoryAdmin primeiro na MRO
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Account Info", {"fields": ("Account", "display_name")}),
        ("Avatar Info", {"fields": ("avatar",)}),
    )
    list_display = ("username", "email", "Account", "is_active", "is_staff", "avatar")
    list_filter = ("Account", "is_active", "is_staff", "is_superuser", "avatar")
    search_fields = ("username", "email", "Account__slug", "Account__display_name")
    ordering = ("Account__slug", "username")


# ------------------- AccountModule -------------------
@admin.register(AccountModule)
class AccountModuleAdmin(SimplyHistoryAdmin):  # ⬅️ histórico
    list_display = (
        "account",
        "module_label",
        "is_enabled",
        "features_short",
        "updated_at",
    )
    list_filter = ("is_enabled", "module", "account")
    search_fields = ("account__slug", "account__display_name")
    readonly_fields = ("created_at", "updated_at")
    fields = ("account", "module", "is_enabled", "features", "created_at", "updated_at")
    ordering = ("account__slug", "module")
    autocomplete_fields = ("account",)

    @admin.display(description="Módulo")
    def module_label(self, obj):
        try:
            return obj.get_module_display()
        except Exception:
            return obj.module or "—"

    @admin.display(description="Features")
    def features_short(self, obj):
        data = obj.features or {}
        if isinstance(data, dict):
            keys = list(data.keys())
            if not keys:
                return "—"
            head = ", ".join(keys[:4])
            return head if len(keys) <= 4 else f"{head}…"
        return "—"


class CustomerAddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 1
    autocomplete_fields = ("address",)
    fields = ("address", "role", "is_primary", "label", "valid_from", "valid_until")
    readonly_fields = ("created_at", "updated_at")


class CustomerContactInline(admin.TabularInline):
    model = CustomerContact
    extra = 1
    autocomplete_fields = ("contact",)
    fields = ("contact", "is_primary", "notes")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Customer)
class CustomerAdmin(SimplyHistoryAdmin):  # ⬅️ histórico
    list_display = (
        "full_name",
        "customer_type",
        "document",
        "primary_email",
        "primary_phone",
        "preferred_store",
        "is_active",
    )
    list_filter = ("customer_type", "is_active", "preferred_store")
    search_fields = (
        "full_name",
        "fantasy_name",
        "document",
        "primary_email",
        "primary_phone",
    )
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("Account", "preferred_store")
    inlines = [CustomerAddressInline, CustomerContactInline]
    fieldsets = (
        (
            "Identificação",
            {
                "fields": (
                    "Account",
                    "customer_type",
                    "full_name",
                    "fantasy_name",
                    "document",
                    "state_registration",
                    "municipal_registration",
                )
            },
        ),
        ("Contatos principais", {"fields": ("primary_email", "primary_phone")}),
        (
            "ERP",
            {"fields": ("payment_term", "credit_limit", "is_blocked", "notes_erp")},
        ),
        (
            "PDV",
            {
                "fields": (
                    "loyalty_code",
                    "preferred_store",
                    "marketing_opt_in",
                    "birth_date",
                )
            },
        ),
        (
            "TMS",
            {
                "fields": (
                    "delivery_notes",
                    "delivery_time_window_start",
                    "delivery_time_window_end",
                    "requires_scheduling",
                    "unloading_requirements",
                )
            },
        ),
        ("Status", {"fields": ("is_active", "created_at", "updated_at")}),
    )


@admin.register(Address)
class AddressAdmin(SimplyHistoryAdmin):  # ⬅️ histórico
    list_display = ("street", "number", "city", "state", "postal_code", "is_active")
    list_filter = ("is_active", "state", "city")
    search_fields = ("street", "number", "city", "postal_code")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CustomerAddress)
class CustomerAddressAdmin(SimplyHistoryAdmin):  # ⬅️ histórico
    list_display = (
        "customer",
        "address",
        "role",
        "is_primary",
        "valid_from",
        "valid_until",
    )
    list_filter = ("role", "is_primary")
    search_fields = ("customer__full_name", "address__street")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ContactType)
class ContactTypeAdmin(SimplyHistoryAdmin):  # ⬅️ histórico
    list_display = ("name", "account", "is_active", "pattern_short", "updated_at")
    list_filter = ("is_active", "account")
    search_fields = ("name", "pattern", "account__slug", "account__display_name")
    ordering = ("account__slug", "name")
    autocomplete_fields = ("account",)
    readonly_fields = ("created_at", "updated_at")
    fields = ("account", "name", "pattern", "is_active", "created_at", "updated_at")

    @admin.display(description="Regex")
    def pattern_short(self, obj):
        p = obj.pattern or ""
        return (p[:60] + "…") if len(p) > 60 else p

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        acc = request.GET.get("Account") or request.GET.get("account")
        if acc and not _is_uuid(acc):
            try:
                initial["account"] = str(Account.objects.only("id").get(slug=acc).pk)
            except Account.DoesNotExist:
                pass
        return initial


class ContactCustomerInline(admin.TabularInline):
    model = CustomerContact
    extra = 0
    autocomplete_fields = ("customer",)
    fields = ("customer", "is_primary", "notes")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Contact)
class ContactAdmin(SimplyHistoryAdmin):  # ⬅️ histórico
    list_display = ("contact_type", "value", "account", "is_verified", "updated_at")
    list_filter = ("is_verified", "contact_type", "account")
    search_fields = (
        "value",
        "contact_type__name",
        "account__slug",
        "account__display_name",
    )
    ordering = ("account__slug", "contact_type__name", "value")
    autocomplete_fields = ("account", "contact_type")
    readonly_fields = ("created_at", "updated_at")
    fields = (
        "account",
        "contact_type",
        "value",
        "is_verified",
        "created_at",
        "updated_at",
    )
    inlines = [ContactCustomerInline]


@admin.register(CustomerContact)
class CustomerContactAdmin(SimplyHistoryAdmin):  # ⬅️ histórico
    list_display = ("customer", "contact", "is_primary", "notes")
    list_filter = ("is_primary",)
    search_fields = ("customer__full_name", "contact__value")
    autocomplete_fields = ("customer", "contact")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Files)
class FilesAdmin(SimplyHistoryAdmin):  # ⬅️ histórico
    list_display = ("label", "Account", "original_name", "created_at")
    search_fields = ("label", "original_name", "Account__slug", "Account__id")
    list_filter = ("Account",)
    readonly_fields = ("created_at", "updated_at", "preview_url")

    def preview_url(self, obj):
        return obj.url

    preview_url.short_description = "URL"
