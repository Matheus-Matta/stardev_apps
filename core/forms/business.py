# account/forms_business.py
from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from core.models import Business, Address

def _to_float_or_none(v):
    if v in (None, ""):
        return None
    try:
        return float(v)
    except (TypeError, ValueError, InvalidOperation):
        return None

def _address_to_dict(addr: Address | None) -> dict | None:
    if not addr:
        return None
    return {
        "id": str(addr.pk),
        "country": addr.country,
        "state": addr.state,
        "city": addr.city,
        "district": addr.district,
        "street": addr.street,
        "number": addr.number,
        "complement": addr.complement,
        "reference": addr.reference,
        "postal_code": addr.postal_code,
        "latitude": _to_float_or_none(addr.latitude),
        "longitude": _to_float_or_none(addr.longitude),
        "place_id": addr.place_id,
        "geohash": addr.geohash,
    }

class BusinessForm(forms.ModelForm):
    """
    Form de Business com endereço em um único campo JSON (`business_address`):
      - Duas formas de informar endereço:
        a) escolher um Address existente no campo `address`
        b) enviar tudo no campo `business_address` (dict/JSON) -> cria/atualiza Address
      - Sempre popula Business.address_json com o Address final.
    """

    address = forms.ModelChoiceField(
        queryset=Address.objects.none(), 
        required=False
    )

    business_address = forms.JSONField(required=False)

    class Meta:
        model = Business
        fields = [
            "parent",
            "code",
            "name",
            "cnpj",
            "business_type",
            "is_active",
            "address",
            "business_address",
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop("account", None)
        super().__init__(*args, **kwargs)

        qs = Address.objects.all()
        if self.account:
            qs = qs.filter(account=self.account)
        self.fields["address"].queryset = qs

        if self.instance and self.instance.pk and self.instance.address_id:
            self.fields["address"].initial = self.instance.address_id

    def clean_cnpj(self):
        """Normaliza/valida o CNPJ. Mantém formato se não tiver 14 dígitos."""
        v = (self.cleaned_data.get("cnpj") or "").strip()
        digits = "".join(ch for ch in v if ch.isdigit())
        if len(digits) != 14:
            return v
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"

    def clean_business_address(self):
        """
        Normaliza o JSON de endereço, se fornecido.
        Campos aceitos: country, state, city, district, street, number,
                        complement, reference, postal_code, latitude, longitude,
                        place_id, geohash.
        """
        data = self.cleaned_data.get("business_address")
        if not data:
            return None
        if not isinstance(data, dict):
            raise ValidationError("business_address deve ser um objeto JSON.")

        normalized = {
            "country":     (data.get("country") or "BR").upper(),
            "state":       (data.get("state") or "").strip(),
            "city":        (data.get("city") or "").strip(),
            "district":    (data.get("district") or "").strip(),
            "street":      (data.get("street") or "").strip(),
            "number":      (data.get("number") or "").strip(),
            "complement":  (data.get("complement") or "").strip(),
            "reference":   (data.get("reference") or "").strip(),
            "postal_code": (data.get("postal_code") or "").replace("-", "").replace(" ", ""),
            "latitude":    _to_float_or_none(data.get("latitude")),
            "longitude":   _to_float_or_none(data.get("longitude")),
            "place_id":    (data.get("place_id") or "").strip(),
            "geohash":     (data.get("geohash") or "").strip(),
        }
        return normalized


    def _has_inline_address(self) -> bool:
        """True se `business_address` foi informado com ao menos um valor relevante."""
        inline = self.cleaned_data.get("business_address")
        if not inline or not isinstance(inline, dict):
            return False
        return any(v not in (None, "", []) for v in inline.values())

    def _collect_inline_address(self) -> dict:
        """Retorna o dict já normalizado em clean_business_address()."""
        return self.cleaned_data.get("business_address") or {}

    def _upsert_address(self, inline: dict) -> Address:
        """
        Cria/atualiza um Address pertencente ao tenant:
        - se instance.address existir, atualiza nele;
        - senão, cria novo para o tenant (self.account é preferencial).
        """
        addr = self.instance.address if (self.instance and self.instance.address_id) else None

        if addr is None:
            # tenta usar a account passada no form; senão, cai para a Account do instance
            if self.account:
                addr = Address(account=self.account)
            else:
                acc = getattr(self.instance, "Account", None)
                addr = Address(account=acc)

        # aplica campos
        for k in (
            "country", "state", "city", "district", "street", "number",
            "complement", "reference", "postal_code", "place_id", "geohash"
        ):
            setattr(addr, k, inline.get(k) or "")

        # latitude/longitude podem ser None
        lat = inline.get("latitude")
        lon = inline.get("longitude")
        addr.latitude = lat
        addr.longitude = lon

        addr.save()
        return addr

    def save(self, commit=True):
        """
        Regras:
        - Se `business_address` foi enviado -> cria/atualiza Address e vincula
        - Senão, usa `address` (ModelChoice) se informado
        - Sempre atualiza `address_json` a partir do Address final (ou None)
        """
        instance: Business = super().save(commit=False)

        if self._has_inline_address():
            data = self._collect_inline_address()
            address_obj = self._upsert_address(data)
        else:
            address_obj = self.cleaned_data.get("address") or instance.address

        instance.address = address_obj
        instance.address_json = _address_to_dict(address_obj) or {}

        if commit:
            instance.save()
            self.save_m2m()

        return instance

    @staticmethod
    def extra_serialize(instance: Business) -> dict:
        """
        Hook para o ModelHelper incorporar dados extras do Business:
        - 'address_data': dict completo do endereço (ou None)
        """
        return {
            "address_data": _address_to_dict(getattr(instance, "address", None))
        }
