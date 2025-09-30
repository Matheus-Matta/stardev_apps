from rest_framework import serializers
from core.models import AccountModule

class AccountModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountModule
        fields = [
            "id",
            "module",
            "features",
            "is_enabled",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        account = getattr(request, "account", None) if request else None
        if account:
            validated_data["account"] = account
        return super().create(validated_data)
