from django import forms
from django.contrib.auth.models import Permission
from core.models import User, Files
import re
class UserForm(forms.ModelForm):
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        required=False,
        help_text="Informe uma senha apenas ao criar o usuário ou se quiser trocar."
    )

    avatar_url = forms.CharField(
        label="Avatar URL",
        required=False,
        disabled=True,
    )

    group_permissions = forms.MultipleChoiceField(
        label="Permissões (herdadas dos grupos)",
        choices=[],          # vamos preencher no __init__
        required=False,
        disabled=True,
        help_text="Permissões concedidas pelos grupos do usuário."
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "Account",
            "avatar",
            "display_name",
            "phone",
            "bio",
            "group_permissions", 
            "is_active",
            "is_superuser",
            "avatar_url",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields.pop("password", None)
            if "Account" in self.fields:
                self.fields["Account"].disabled = True

        if self.instance and getattr(self.instance, "avatar", None):
            try:
                self.fields["avatar_url"].initial = getattr(self.instance.avatar, "url", None)
            except Exception:
                self.fields["avatar_url"].initial = None

        perms = Permission.objects.select_related("content_type").all()
        self.fields["group_permissions"].choices = [
            (
                p.codename,
                f"{p.content_type.app_label}.{p.codename} — {p.name}"
            )
            for p in perms
        ]

        if self.instance and self.instance.pk:
            group_perms_qs = Permission.objects.filter(
                group__in=self.instance.groups.all()
            ).select_related("content_type").distinct()

            initial_codenames = list(group_perms_qs.values_list("codename", flat=True))
            self.fields["group_permissions"].initial = initial_codenames
        else:
            self.fields["group_permissions"].initial = []
            
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            digits = re.sub(r"\D", "", phone)
            if not (10 <= len(digits) <= 14):
                raise forms.ValidationError(
                    "Telefone inválido. O número deve ter entre 10 e 14 dígitos."
                )
            phone_normalizado = f"+{digits}"
            if not re.fullmatch(r"^\+\d{10,14}$", phone_normalizado):
                raise forms.ValidationError(
                    "Telefone inválido. Use o formato: +5521912345678 (código do país + DDD + número)."
                )
            return phone_normalizado
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            qs = User.objects.filter(email__iexact=email)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Este e-mail já está sendo utilizado por outro usuário.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user
