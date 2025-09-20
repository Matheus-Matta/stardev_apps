from django import forms
from core.models import User, Files

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
        return user
