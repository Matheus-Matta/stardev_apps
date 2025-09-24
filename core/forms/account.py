from django import forms
from django.core.exceptions import ValidationError
from core.models import Account
import re

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            "slug",
            "legal_name",
            "display_name",
            "time_zone",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip().lower()

        if not (3 <= len(slug) <= 80):
            raise ValidationError("Slug deve ter entre 3 e 80 caracteres.")

        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValidationError(
                "Slug inválido. Use letras minúsculas, números e hífens (sem iniciar/terminar com hífen)."
            )

        RESERVED = {"admin", "api", "static", "media", "root", "null", "none"}
        if slug in RESERVED:
            raise ValidationError("Este slug é reservado. Escolha outro.")

        qs = Account.objects.filter(slug=slug)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Já existe uma conta com este slug.")

        return slug

    def clean_display_name(self):
        name = (self.cleaned_data.get("display_name") or "").strip()
        if not (2 <= len(name) <= 255):
            raise ValidationError("Nome de exibição deve ter entre 2 e 255 caracteres.")
        return " ".join(name.split())

    def clean_legal_name(self):
        legal = (self.cleaned_data.get("legal_name") or "").strip()
        if not (2 <= len(legal) <= 255):
            raise ValidationError("Razão social deve ter entre 2 e 255 caracteres.")
        return " ".join(legal.split())

    def clean(self):
        cleaned = super().clean()
        return cleaned
