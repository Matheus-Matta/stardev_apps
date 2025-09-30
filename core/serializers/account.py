# account/serializers/account.py
from rest_framework import serializers
from core.models import Account 

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "slug",
            "legal_name",
            "display_name",
            "email_principal",
            "phone_principal",
            "site_url",
            "logo_url",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "email_principal": {"required": False, "allow_null": True, "allow_blank": True},
            "phone_principal": {"required": False, "allow_null": True, "allow_blank": True},
            "site_url":        {"required": False, "allow_null": True, "allow_blank": True},
            "logo_url":        {"required": False, "allow_null": True, "allow_blank": True},
            "time_zone":       {"required": False},
            "display_name":    {"required": False},
            "legal_name":      {"required": False},
            "slug":            {"required": False},
        }

    def validate_slug(self, value: str) -> str:
        return (value or "").lower()

    def validate(self, attrs):
        def none_if_blank(v):
            return None if isinstance(v, str) and v.strip() == "" else v

        for key in ("email_principal", "phone_principal", "site_url", "logo_url"):
            if key in attrs:
                attrs[key] = none_if_blank(attrs[key])
        return attrs

    def create(self, validated_data):
        raise serializers.ValidationError("Criação de Account via API não é permitida.")

    def update(self, instance: Account, validated_data):
        allowed = {
            "slug",
            "legal_name",
            "display_name",
            "time_zone",
            "email_principal",
            "phone_principal",
            "site_url",
            "logo_url",
            "is_active",
        }
        for field, val in validated_data.items():
            if field not in allowed:
                continue
            if field == "slug" and isinstance(val, str):
                val = val.lower()
            setattr(instance, field, val)
        instance.save()
        return instance
