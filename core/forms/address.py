# account/forms_address.py
from django import forms
from core.models import Address

class AddressForm(forms.ModelForm):
    """
    Address:
    - expõe somente campos “negociais”
    - normaliza CEP (postal_code) => apenas dígitos
    """
    class Meta:
        model = Address
        fields = [
            "country", "state", "city", "district",
            "street", "number", "complement", "reference",
            "postal_code", "latitude", "longitude",
            "place_id", "geohash", "is_active",
        ]
        # 'account', 'id', 'created_at', 'updated_at' ficam de fora (multi-tenant / sistema)

    def clean_postal_code(self):
        v = self.cleaned_data.get("postal_code") or ""
        v = "".join(ch for ch in v if ch.isdigit())
        return v or None
