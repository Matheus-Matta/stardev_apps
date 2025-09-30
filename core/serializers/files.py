from rest_framework import serializers
from django.core.files.uploadedfile import UploadedFile
from django.core.files.base import File as DjangoFile
from django.db.models.fields.files import FieldFile
from core.models import Files
from core.utils.normalize_url_media import normalize_url_media


class FileInfoField(serializers.Field):
    """
    Representa FileField como {"name","url"} na saída,
    e aceita uploads (UploadedFile/FieldFile) na entrada.
    """

    def to_representation(self, value):
        if not isinstance(value, FieldFile) or not value:
            return None
        try:
            url = normalize_url_media(getattr(value, "url", None))
        except Exception:
            url = None
        return {"name": getattr(value, "name", None), "url": url}

    def _coerce_one(self, data):
        if isinstance(data, (UploadedFile, DjangoFile, FieldFile)):
            return data
        if hasattr(data, "read") and hasattr(data, "name"):
            return data
        return None

    def to_internal_value(self, data):
        if data is None or data == "":
            return None

        if isinstance(data, (list, tuple)):
            for item in data:
                coerced = self._coerce_one(item)
                if coerced is not None:
                    return coerced
            raise serializers.ValidationError("Formato inválido para arquivo. Envie multipart/form-data com o campo do arquivo.")

        if isinstance(data, dict):
            for key in ("file", "upload", "value"):
                coerced = self._coerce_one(data.get(key))
                if coerced is not None:
                    return coerced
            if any(k in data for k in ("file", "upload", "value")):
                return None
            raise serializers.ValidationError("Formato inválido para arquivo. Envie multipart/form-data com o campo do arquivo.")

        # objeto único
        coerced = self._coerce_one(data)
        if coerced is not None:
            return coerced

        raise serializers.ValidationError("Formato inválido para arquivo. Envie multipart/form-data com o campo do arquivo.")


class FilesMiniSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Files
        fields = ["id", "label", "original_name", "url"]
        read_only_fields = fields

    def get_url(self, obj):
        try:
            return normalize_url_media(getattr(obj.file, "url", None))
        except Exception:
            return None


class FilesSerializer(serializers.ModelSerializer):
    file = FileInfoField()

    class Meta:
        model = Files
        fields = [
            "id",
            "label",
            "file",
            "original_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "original_name", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        account = getattr(request, "account", None) if request else None
        if account:
            validated_data["Account"] = account
        f = validated_data.get("file")
        if isinstance(f, (UploadedFile, DjangoFile, FieldFile)) and not validated_data.get("original_name"):
            validated_data["original_name"] = getattr(f, "name", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("Account", None)
        validated_data.pop("Account_id", None)
        f = validated_data.get("file")
        if isinstance(f, (UploadedFile, DjangoFile, FieldFile)):
            validated_data.setdefault("original_name", getattr(f, "name", None))
        return super().update(instance, validated_data)
