from rest_framework import serializers
from django.db.models import Q
from django.contrib.auth.models import Permission
from core.models import User
from .files import FilesMiniSerializer

class UserSerializer(serializers.ModelSerializer):
    avatar = FilesMiniSerializer(read_only=True)
    avatar_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    groups_permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username", "email", "first_name", "last_name",
            "display_name", "phone", "bio",
            "is_active", "is_superuser",
            "avatar",
            "avatar_id",
            "groups_permissions",
            "date_joined",
            "last_login",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "avatar", "groups_permissions",
            "date_joined", "last_login", "created_at", "updated_at"
        ]

    def get_groups_permissions(self, obj: User):
        """
        Retorna apenas uma lista de codenames únicos
        vindos dos grupos + permissões diretas.
        """
        qs = (
            Permission.objects
            .filter(Q(group__user=obj) | Q(user=obj))
            .distinct()
            .order_by("codename")
        )
        return list(qs.values_list("codename", flat=True))

    def create(self, validated_data):
        request = self.context.get("request")
        account = getattr(request, "account", None) if request else None

        avatar_id = validated_data.pop("avatar_id", None)
        obj = User(**validated_data)
        if account:
            obj.Account = account
        if avatar_id:
            obj.avatar_id = avatar_id
        if "password" in validated_data:
            obj.set_password(validated_data.get("password") or None)
        obj.save()
        return obj

    def update(self, instance: User, validated_data):
        avatar_id = validated_data.pop("avatar_id", None)
        for attr, val in validated_data.items():
            if attr == "password":
                instance.set_password(val)
            else:
                setattr(instance, attr, val)
        if avatar_id is not None:
            instance.avatar_id = avatar_id
        instance.save()
        return instance
