from django import forms
from core.models import Account

class AccountForm(forms.ModelForm):
    """
    Formulário para criação e atualização de Account
    """
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
        if self.instance and self.instance.pk:
            self.fields["slug"].disabled = True
