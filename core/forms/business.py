# account/forms_business.py
from django import forms
from core.models import Business

class BusinessForm(forms.ModelForm):
    """
    Business:
    - não permite editar Account via API
    - opcionalmente normaliza CNPJ (apenas dígitos; validação extra pode ser incluída)
    """
    class Meta:
        model = Business
        fields = [
            "parent",
            "code", "name", "cnpj",
            "business_type",
            "address_json",
            "is_active",
        ]

    def clean_cnpj(self):
        v = (self.cleaned_data.get("cnpj") or "").strip()
        digits = "".join(ch for ch in v if ch.isdigit())
        if len(digits) != 14:
            return v  
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
