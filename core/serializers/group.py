# account/serializers/group.py
from rest_framework import serializers
from django.contrib.auth.models import Group

class GroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="account_bind.name", read_only=True)

    class Meta:
        model = Group
        fields = ["id", "name"]
        read_only_fields = ["id", "name"]


class GroupCreateUpdateSerializer(serializers.Serializer):
    """
    Cria/renomeia grupos do tenant via AccountGroup.
    """
    name = serializers.CharField(max_length=150)

    def create(self, validated_data):
        request = self.context.get("request")
        account = getattr(request, "account", None) if request else None
        if not account:
            raise serializers.ValidationError("Account ausente no contexto.")
        from core.models import AccountGroup
        ag = AccountGroup.create_with_group(account=account, name=validated_data["name"])
        return ag.group

    def update(self, instance: Group, validated_data):
        ag = getattr(instance, "account_bind", None)
        if not ag:
            raise serializers.ValidationError("Group sem vínculo de tenant.")
        ag.name = validated_data["name"]
        ag.save(update_fields=["name"])
        return instance
