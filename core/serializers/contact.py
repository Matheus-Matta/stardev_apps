from rest_framework import serializers
from core.models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "type",
            "value",
            "is_verified",
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
