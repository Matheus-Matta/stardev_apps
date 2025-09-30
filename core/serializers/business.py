from rest_framework import serializers
from core.models import Business , Address
from .address import AddressSerializer

def _to_float_or_none(v):
    if v in (None, ""):
        return None
    try:
        return float(v)
    except Exception:
        return None

def _address_to_dict(addr: Address | None) -> dict:
    if not addr:
        return {}
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

def _normalize_cnpj(value: str) -> str:
    v = (value or "").strip()
    digits = "".join(ch for ch in v if ch.isdigit())
    if len(digits) != 14:
        return v
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"

class BusinessMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ["id", "code", "name", "business_type", "is_active"]
        read_only_fields = fields

class BusinessSerializer(serializers.ModelSerializer):
    # sub-itens (sem Account)
    address  = AddressSerializer(read_only=True)
    parent   = BusinessMiniSerializer(read_only=True)
    children = BusinessMiniSerializer(read_only=True, many=True)

    address_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    parent_id  = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Business
        fields = [
            "id",
            "code",
            "name",
            "cnpj",
            "business_type",
            "is_active",
            "address",       
            "address_id",    
            "parent",         
            "parent_id",     
            "children",      
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "address", "parent", "children", "created_at", "updated_at"]

    def validate_cnpj(self, value: str) -> str:
        return _normalize_cnpj(value)

    def _apply_fk_ids_and_snapshot(self, instance: Business, validated: dict) -> None:
        addr_id = validated.pop("address_id", serializers.empty)
        par_id  = validated.pop("parent_id",  serializers.empty)

        if addr_id is not serializers.empty:
            instance.address_id = addr_id
        if par_id is not serializers.empty:
            instance.parent_id = par_id

    def create(self, validated):
        request = self.context.get("request")
        account = getattr(request, "account", None) if request else None
        if account:
            validated["Account"] = account

        obj = Business(
            Account       = validated.get("Account"),
            code          = validated.get("code"),
            name          = validated.get("name"),
            cnpj          = validated.get("cnpj"),
            business_type = validated.get("business_type"),
            is_active     = validated.get("is_active", True),
        )
        self._apply_fk_ids_and_snapshot(obj, validated)
        obj.save()
        return obj

    def update(self, instance: Business, validated):
        for attr in ("code", "name", "cnpj", "business_type", "is_active"):
            if attr in validated:
                setattr(instance, attr, validated[attr])
        self._apply_fk_ids_and_snapshot(instance, validated)
        instance.save()
        return instance
