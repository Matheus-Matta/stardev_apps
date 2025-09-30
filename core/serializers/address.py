from rest_framework import serializers
from core.models import Address

def _to_float_or_none(v):
    if v in (None, ""):
        return None
    try:
        return float(v)
    except Exception:
        return None

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "country", "state", "city", "district",
            "street", "number", "complement", "reference",
            "postal_code",
            "latitude", "longitude",
            "place_id", "geohash",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        account = getattr(request, "account", None) if request else None
        if account:
            validated_data["account"] = account
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["latitude"]  = _to_float_or_none(data.get("latitude"))
        data["longitude"] = _to_float_or_none(data.get("longitude"))
        return data
